"""
Base Tool Framework
===================

Abstract base class and utilities for AI tools.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="BaseTool")


class ToolCategory(str, Enum):
    """Categories of tools"""

    MONITORING = "monitoring"
    SCALING = "scaling"
    CONFIG = "config"
    ANALYSIS = "analysis"
    HEALING = "healing"


class ToolRiskLevel(str, Enum):
    """Risk level of tool execution"""

    SAFE = "safe"  # Read-only, no side effects
    LOW = "low"  # Minor changes, easily reversible
    MEDIUM = "medium"  # Significant changes, may need review
    HIGH = "high"  # Major changes, requires approval


@dataclass
class ToolResult:
    """Result of tool execution"""

    success: bool
    tool_name: str
    data: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    error: str | None = None
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "tool_name": self.tool_name,
            "data": self.data,
            "message": self.message,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ToolDefinition:
    """Tool definition for registration"""

    name: str
    description: str
    category: ToolCategory
    risk_level: ToolRiskLevel
    parameters_schema: dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = False
    cooldown_seconds: int = 0


class BaseTool(ABC):
    """
    Base class for all AI tools.

    Tools are executable actions that the AI can invoke to:
    - Gather information (monitoring)
    - Make changes (scaling, config)
    - Analyze data (patterns, anomalies)

    Example:
        class HealthCheckTool(BaseTool):
            @property
            def definition(self) -> ToolDefinition:
                return ToolDefinition(
                    name="health_check",
                    description="Check worker health status",
                    category=ToolCategory.MONITORING,
                    risk_level=ToolRiskLevel.SAFE,
                )

            async def execute(self, **params) -> ToolResult:
                # Implementation
                pass
    """

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Get tool definition"""

    @abstractmethod
    async def execute(self, **params: Any) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            **params: Tool-specific parameters

        Returns:
            ToolResult with execution outcome
        """

    async def validate_params(self, **params: Any) -> tuple[bool, str]:
        """
        Validate parameters before execution.

        Override for custom validation.
        """
        return True, ""

    def can_execute(self, approval_mode: str) -> bool:
        """Check if tool can execute given current approval mode"""
        if self.definition.risk_level == ToolRiskLevel.SAFE:
            return True

        if approval_mode == "auto":
            return self.definition.risk_level in [ToolRiskLevel.SAFE, ToolRiskLevel.LOW]
        elif approval_mode == "review":
            return not self.definition.requires_approval
        elif approval_mode == "approval":
            return False  # Always needs approval
        else:  # disabled
            return False


class ToolRegistry:
    """
    Registry for all available AI tools.

    Singleton pattern - one registry for the system.
    """

    _instance: "ToolRegistry | None" = None

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._tools: dict[str, BaseTool] = {}
        self._execution_history: list[ToolResult] = []
        self._last_execution: dict[str, datetime] = {}
        self._initialized = True

        logger.info("🔧 Tool Registry initialized")

    def register(self, tool: BaseTool) -> bool:
        """Register a tool"""
        try:
            name = tool.definition.name
            if name in self._tools:
                logger.warning(f"Tool {name} already registered, overwriting")

            self._tools[name] = tool
            logger.info(f"✅ Registered tool: {name} ({tool.definition.category.value})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register tool: {e}")
            return False

    def get(self, name: str) -> BaseTool | None:
        """Get a tool by name"""
        return self._tools.get(name)

    def list_tools(
        self,
        category: ToolCategory | None = None,
        risk_level: ToolRiskLevel | None = None,
    ) -> list[ToolDefinition]:
        """List all tools, optionally filtered"""
        tools = list(self._tools.values())

        if category:
            tools = [t for t in tools if t.definition.category == category]

        if risk_level:
            tools = [t for t in tools if t.definition.risk_level == risk_level]

        return [t.definition for t in tools]

    async def execute_tool(
        self,
        name: str,
        approval_mode: str = "review",
        **params: Any,
    ) -> ToolResult:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            approval_mode: Current AI approval mode
            **params: Tool parameters

        Returns:
            ToolResult
        """
        import time

        start = time.time()

        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                tool_name=name,
                error=f"Tool '{name}' not found",
            )

        # Check if can execute
        if not tool.can_execute(approval_mode):
            return ToolResult(
                success=False,
                tool_name=name,
                error=f"Tool requires approval (risk: {tool.definition.risk_level.value})",
            )

        # Check cooldown
        last_exec = self._last_execution.get(name)
        if last_exec and tool.definition.cooldown_seconds > 0:
            elapsed = (datetime.utcnow() - last_exec).total_seconds()
            if elapsed < tool.definition.cooldown_seconds:
                return ToolResult(
                    success=False,
                    tool_name=name,
                    error=f"Tool on cooldown ({tool.definition.cooldown_seconds - elapsed:.0f}s remaining)",
                )

        # Validate params
        valid, error = await tool.validate_params(**params)
        if not valid:
            return ToolResult(
                success=False,
                tool_name=name,
                error=f"Invalid parameters: {error}",
            )

        try:
            result = await tool.execute(**params)
            result.execution_time_ms = int((time.time() - start) * 1000)

            # Track execution
            self._last_execution[name] = datetime.utcnow()
            self._execution_history.append(result)

            # Keep history manageable
            if len(self._execution_history) > 1000:
                self._execution_history = self._execution_history[-500:]

            return result

        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return ToolResult(
                success=False,
                tool_name=name,
                error=str(e),
                execution_time_ms=int((time.time() - start) * 1000),
            )

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics"""
        by_category = {}
        by_risk = {}

        for tool in self._tools.values():
            cat = tool.definition.category.value
            risk = tool.definition.risk_level.value

            by_category[cat] = by_category.get(cat, 0) + 1
            by_risk[risk] = by_risk.get(risk, 0) + 1

        return {
            "total_tools": len(self._tools),
            "by_category": by_category,
            "by_risk_level": by_risk,
            "total_executions": len(self._execution_history),
            "recent_executions": [r.to_dict() for r in self._execution_history[-10:]],
        }


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return ToolRegistry()
