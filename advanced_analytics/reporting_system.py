"""
📋 Automated Reporting System - Module 4.5

Enterprise-grade automated reporting with scheduling,
multi-format export, email delivery, and customizable templates.
"""

import asyncio
import json
import logging
import os
import smtplib
import threading
import time
from collections.abc import Callable
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import numpy as np
import pandas as pd
from jinja2 import Template

# Scheduling
try:
    import schedule

    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

# Report generation libraries
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Excel reporting
try:
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# Scheduling
try:
    import schedule

    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

from .ai_insights import AIInsightsGenerator
from .dashboard import VisualizationEngine

# Import our analytics modules
from .data_processor import AdvancedDataProcessor
from .predictive_engine import PredictiveAnalyticsEngine

logger = logging.getLogger(__name__)


class ReportTemplate:
    """📄 Report Template Definition"""

    def __init__(
        self,
        name: str,
        template_type: str = "standard",
        sections: list[str] | None = None,
        styling: dict[str, Any] | None = None,
    ):
        self.name = name
        self.template_type = template_type
        self.sections = sections or [
            "executive_summary",
            "key_metrics",
            "data_analysis",
            "insights",
            "recommendations",
            "appendix",
        ]
        self.styling = styling or self._get_default_styling()
        self.created_at = datetime.now()

    def _get_default_styling(self) -> dict[str, Any]:
        """Get default styling configuration"""
        return {
            "colors": {
                "primary": "#1f77b4",
                "secondary": "#ff7f0e",
                "success": "#2ca02c",
                "warning": "#ff7f0e",
                "danger": "#d62728",
            },
            "fonts": {
                "title": {"family": "Arial", "size": 16, "bold": True},
                "heading": {"family": "Arial", "size": 14, "bold": True},
                "body": {"family": "Arial", "size": 11, "bold": False},
                "caption": {"family": "Arial", "size": 9, "bold": False},
            },
            "layout": {
                "margin_top": 1.0,
                "margin_bottom": 1.0,
                "margin_left": 1.0,
                "margin_right": 1.0,
            },
        }


class AutomatedReportingSystem:
    """
    📊 Automated Reporting System

    Enterprise capabilities:
    - Multi-format reports (PDF, Excel, HTML, JSON)
    - Customizable templates and styling
    - Scheduled report generation
    - Email delivery with attachments
    - Interactive dashboards integration
    - Automated insights inclusion
    """

    def __init__(self, output_directory: str = "./reports"):
        self.output_directory = output_directory
        self.templates = {}
        self.scheduled_reports = {}
        self.email_config = None
        self.report_history = []

        # Initialize analytics engines
        self.data_processor = AdvancedDataProcessor()
        self.predictive_engine = PredictiveAnalyticsEngine()
        self.viz_engine = VisualizationEngine()
        self.insights_generator = AIInsightsGenerator()

        # Create output directory
        os.makedirs(output_directory, exist_ok=True)

        # Initialize scheduler
        self.scheduler_thread = None
        self.is_scheduler_running = False

    def create_template(
        self,
        template_name: str,
        template_type: str = "business_intelligence",
        sections: list[str] | None = None,
        styling: dict[str, Any] | None = None,
    ) -> ReportTemplate:
        """
        📝 Create Custom Report Template

        Args:
            template_name: Unique template identifier
            template_type: Template category
            sections: Report sections to include
            styling: Custom styling configuration

        Returns:
            ReportTemplate object
        """
        template = ReportTemplate(
            name=template_name,
            template_type=template_type,
            sections=sections,
            styling=styling,
        )

        self.templates[template_name] = template
        logger.info(f"Created report template: {template_name}")

        return template

    async def generate_comprehensive_report(
        self,
        data_source: pd.DataFrame | dict[str, pd.DataFrame],
        template_name: str = "default",
        report_title: str = "Analytics Report",
        output_formats: list[str] = ["pdf", "html"],
        include_insights: bool = True,
        include_predictions: bool = True,
    ) -> dict[str, str]:
        """
        📊 Generate Comprehensive Analytics Report

        Args:
            data_source: DataFrame or dict of DataFrames
            template_name: Template to use
            report_title: Report title
            output_formats: List of output formats
            include_insights: Include AI-generated insights
            include_predictions: Include predictive analytics

        Returns:
            Dictionary mapping format to file path
        """
        try:
            logger.info(f"Generating comprehensive report: {report_title}")

            # Ensure we have a template
            if template_name not in self.templates:
                self.create_template(template_name)

            template = self.templates[template_name]

            # Prepare data
            if isinstance(data_source, pd.DataFrame):
                main_df = data_source
                data_dict = {"main": data_source}
            else:
                main_df = list(data_source.values())[0]
                data_dict = data_source

            # Generate report content
            report_content = await self._generate_report_content(
                data_dict, template, report_title, include_insights, include_predictions
            )

            # Generate reports in different formats
            output_files = {}
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{report_title.replace(' ', '_')}_{timestamp}"

            for format_type in output_formats:
                if format_type == "pdf":
                    filepath = await self._generate_pdf_report(
                        report_content, base_filename
                    )
                elif format_type == "html":
                    filepath = await self._generate_html_report(
                        report_content, base_filename
                    )
                elif format_type == "excel":
                    filepath = await self._generate_excel_report(
                        report_content, data_dict, base_filename
                    )
                elif format_type == "json":
                    filepath = await self._generate_json_report(
                        report_content, base_filename
                    )
                else:
                    logger.warning(f"Unsupported format: {format_type}")
                    continue

                output_files[format_type] = filepath

            # Record report generation
            report_record = {
                "title": report_title,
                "template": template_name,
                "timestamp": datetime.now().isoformat(),
                "formats": list(output_files.keys()),
                "files": output_files,
                "data_shape": main_df.shape if main_df is not None else None,
            }

            self.report_history.append(report_record)

            logger.info(f"Report generation complete: {len(output_files)} formats")
            return output_files

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise

    async def schedule_report(
        self,
        report_name: str,
        data_source_func: Callable,
        schedule_pattern: str,
        template_name: str = "default",
        output_formats: list[str] = ["pdf"],
        email_recipients: list[str] | None = None,
        report_config: dict[str, Any] | None = None,
    ) -> str:
        """
        ⏰ Schedule Automated Report Generation

        Args:
            report_name: Unique report identifier
            data_source_func: Function that returns data for the report
            schedule_pattern: Schedule pattern (e.g., 'daily', 'weekly', 'monthly')
            template_name: Template to use
            output_formats: Output formats
            email_recipients: Email addresses for delivery
            report_config: Additional configuration

        Returns:
            Schedule ID
        """
        try:
            schedule_id = f"{report_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            scheduled_report = {
                "id": schedule_id,
                "name": report_name,
                "data_source_func": data_source_func,
                "schedule_pattern": schedule_pattern,
                "template_name": template_name,
                "output_formats": output_formats,
                "email_recipients": email_recipients,
                "config": report_config or {},
                "created_at": datetime.now().isoformat(),
                "last_run": None,
                "next_run": None,
                "is_active": True,
            }

            self.scheduled_reports[schedule_id] = scheduled_report

            # Add to scheduler
            self._add_to_scheduler(scheduled_report)

            # Start scheduler if not running
            if not self.is_scheduler_running:
                self.start_scheduler()

            logger.info(f"Scheduled report: {report_name} ({schedule_pattern})")
            return schedule_id

        except Exception as e:
            logger.error(f"Report scheduling failed: {str(e)}")
            raise

    def configure_email(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        sender_email: str,
        use_tls: bool = True,
    ):
        """📧 Configure Email Settings for Report Delivery"""
        self.email_config = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "sender_email": sender_email,
            "use_tls": use_tls,
        }
        logger.info(f"Email configuration updated for {smtp_server}")

    async def send_report_email(
        self,
        recipients: list[str],
        subject: str,
        message: str,
        attachments: list[str] | None = None,
    ) -> bool:
        """📧 Send Report via Email"""
        try:
            if not self.email_config:
                raise ValueError(
                    "Email configuration not set. Use configure_email() first."
                )

            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.email_config["sender_email"]
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject

            # Add body
            msg.attach(MIMEText(message, "plain"))

            # Add attachments
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(filepath)}",
                        )
                        msg.attach(part)

            # Send email
            server = smtplib.SMTP(
                self.email_config["smtp_server"], self.email_config["smtp_port"]
            )

            if self.email_config["use_tls"]:
                server.starttls()

            server.login(self.email_config["username"], self.email_config["password"])
            server.sendmail(
                self.email_config["sender_email"], recipients, msg.as_string()
            )
            server.quit()

            logger.info(f"Report email sent to {len(recipients)} recipients")
            return True

        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return False

    def start_scheduler(self):
        """⏰ Start Report Scheduler"""
        if not self.is_scheduler_running:
            self.is_scheduler_running = True
            self.scheduler_thread = threading.Thread(
                target=self._run_scheduler, daemon=True
            )
            self.scheduler_thread.start()
            logger.info("Report scheduler started")

    def stop_scheduler(self):
        """⏹️ Stop Report Scheduler"""
        self.is_scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Report scheduler stopped")

    def get_report_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """📜 Get Report Generation History"""
        return self.report_history[-limit:]

    def get_scheduled_reports(self) -> dict[str, dict[str, Any]]:
        """⏰ Get Scheduled Reports Status"""
        return self.scheduled_reports

    # Private helper methods
    async def _generate_report_content(
        self,
        data_dict: dict[str, pd.DataFrame],
        template: ReportTemplate,
        report_title: str,
        include_insights: bool,
        include_predictions: bool,
    ) -> dict[str, Any]:
        """Generate report content based on template"""
        content = {
            "title": report_title,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "template_name": template.name,
            "sections": {},
        }

        main_df = list(data_dict.values())[0]

        # Executive Summary
        if "executive_summary" in template.sections:
            content["sections"][
                "executive_summary"
            ] = await self._generate_executive_summary(main_df)

        # Key Metrics
        if "key_metrics" in template.sections:
            content["sections"]["key_metrics"] = await self._generate_key_metrics(
                main_df
            )

        # Data Analysis
        if "data_analysis" in template.sections:
            content["sections"]["data_analysis"] = await self._generate_data_analysis(
                main_df
            )

        # AI Insights
        if "insights" in template.sections and include_insights:
            content["sections"]["insights"] = await self._generate_insights_section(
                main_df
            )

        # Predictions
        if "predictions" in template.sections and include_predictions:
            content["sections"][
                "predictions"
            ] = await self._generate_predictions_section(main_df)

        # Recommendations
        if "recommendations" in template.sections:
            content["sections"][
                "recommendations"
            ] = await self._generate_recommendations_section(main_df)

        return content

    async def _generate_executive_summary(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate executive summary section"""
        return {
            "title": "Executive Summary",
            "content": {
                "overview": f"Analysis of dataset containing {len(df):,} records across {len(df.columns)} dimensions.",
                "key_findings": [
                    f"Dataset spans {len(df):,} observations",
                    f"Contains {len(df.columns)} variables",
                    f"Data completeness: {(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))):.1%}",
                ],
                "timeframe": f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            },
        }

    async def _generate_key_metrics(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate key metrics section"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        metrics = {"title": "Key Performance Indicators", "metrics": []}

        if len(numeric_cols) > 0:
            for col in numeric_cols[:5]:  # Top 5 numeric columns
                col_stats = df[col].describe()
                metrics["metrics"].append(
                    {
                        "name": col.replace("_", " ").title(),
                        "value": col_stats["mean"],
                        "change": "N/A",  # Would need historical data
                        "trend": "stable",
                        "format": ",.2f",
                    }
                )

        return metrics

    async def _generate_data_analysis(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate data analysis section"""
        analysis = {
            "title": "Data Analysis",
            "content": {
                "data_overview": {
                    "total_records": len(df),
                    "total_columns": len(df.columns),
                    "data_types": df.dtypes.value_counts().to_dict(),
                    "missing_data": df.isnull().sum().to_dict(),
                },
                "statistical_summary": (
                    df.describe(include="all").to_dict()
                    if len(df.select_dtypes(include=[np.number]).columns) > 0
                    else {}
                ),
                "data_quality": {
                    "completeness": (
                        1 - df.isnull().sum().sum() / (len(df) * len(df.columns))
                    )
                    * 100,
                    "uniqueness": (
                        len(df) / len(df.drop_duplicates()) * 100
                        if len(df) > 0
                        else 100
                    ),
                    "consistency": 95.0,  # Placeholder - would need actual consistency checks
                },
            },
        }

        return analysis

    async def _generate_insights_section(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate AI insights section"""
        try:
            insights = await self.insights_generator.generate_comprehensive_insights(df)

            return {
                "title": "AI-Powered Insights",
                "content": {
                    "summary": insights.get(
                        "narrative_summary", "No insights available"
                    ),
                    "key_insights": insights.get("insights", {}),
                    "confidence_scores": insights.get("confidence_scores", {}),
                    "recommendations": insights.get("recommendations", []),
                },
            }
        except Exception as e:
            logger.warning(f"Insights generation failed: {str(e)}")
            return {
                "title": "AI-Powered Insights",
                "content": {"error": "Insights generation not available"},
            }

    async def _generate_predictions_section(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate predictions section"""
        try:
            # Simple prediction example - would be customized based on data
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                target_col = numeric_cols[0]
                prediction_results = await self.predictive_engine.auto_predict(
                    df, target_col, test_size=0.1
                )

                return {
                    "title": "Predictive Analytics",
                    "content": {
                        "best_model": prediction_results.get("best_model", "N/A"),
                        "model_score": prediction_results.get("best_model_score", 0),
                        "feature_importance": prediction_results.get(
                            "feature_importance", {}
                        ),
                        "metrics": prediction_results.get("metrics", {}),
                    },
                }
            else:
                return {
                    "title": "Predictive Analytics",
                    "content": {"message": "Insufficient numeric data for predictions"},
                }
        except Exception as e:
            logger.warning(f"Predictions generation failed: {str(e)}")
            return {
                "title": "Predictive Analytics",
                "content": {"error": "Predictions not available"},
            }

    async def _generate_recommendations_section(
        self, df: pd.DataFrame
    ) -> dict[str, Any]:
        """Generate recommendations section"""
        recommendations = []

        # Data quality recommendations
        missing_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        if missing_percentage > 5:
            recommendations.append(
                f"Address missing data: {missing_percentage:.1f}% of data is missing"
            )

        # Performance recommendations
        if len(df) < 1000:
            recommendations.append(
                "Consider collecting more data for robust statistical analysis"
            )

        # General recommendations
        recommendations.append("Implement regular data quality monitoring")
        recommendations.append(
            "Consider automating this analysis with scheduled reports"
        )

        return {
            "title": "Recommendations",
            "content": {
                "action_items": recommendations,
                "priority": "high" if missing_percentage > 20 else "medium",
                "next_steps": [
                    "Review data collection processes",
                    "Implement data validation rules",
                    "Schedule regular analysis updates",
                ],
            },
        }

    async def _generate_pdf_report(
        self, content: dict[str, Any], base_filename: str
    ) -> str:
        """Generate PDF report"""
        try:
            filepath = os.path.join(self.output_directory, f"{base_filename}.pdf")

            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # Center alignment
            )
            story.append(Paragraph(content["title"], title_style))
            story.append(Spacer(1, 12))

            # Generated timestamp
            story.append(
                Paragraph(f"Generated: {content['generated_at']}", styles["Normal"])
            )
            story.append(Spacer(1, 20))

            # Sections
            for section_name, section_data in content["sections"].items():
                if isinstance(section_data, dict) and "title" in section_data:
                    # Section title
                    story.append(Paragraph(section_data["title"], styles["Heading2"]))
                    story.append(Spacer(1, 12))

                    # Section content
                    if "content" in section_data:
                        section_content = section_data["content"]
                        if isinstance(section_content, str):
                            story.append(Paragraph(section_content, styles["Normal"]))
                        elif isinstance(section_content, dict):
                            for key, value in section_content.items():
                                if isinstance(value, (str, int, float)):
                                    story.append(
                                        Paragraph(
                                            f"<b>{key.replace('_', ' ').title()}:</b> {value}",
                                            styles["Normal"],
                                        )
                                    )
                                elif isinstance(value, list):
                                    story.append(
                                        Paragraph(
                                            f"<b>{key.replace('_', ' ').title()}:</b>",
                                            styles["Normal"],
                                        )
                                    )
                                    for item in value[:5]:  # Limit to 5 items
                                        story.append(
                                            Paragraph(f"• {item}", styles["Normal"])
                                        )

                    story.append(Spacer(1, 20))

            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise

    async def _generate_html_report(
        self, content: dict[str, Any], base_filename: str
    ) -> str:
        """Generate HTML report"""
        try:
            filepath = os.path.join(self.output_directory, f"{base_filename}.html")

            # HTML template
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 5px; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
        .recommendation { background-color: #e7f3ff; padding: 10px; margin: 5px 0; border-radius: 5px; }
        ul { list-style-type: disc; margin-left: 20px; }
        .timestamp { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p class="timestamp">Generated: {{ generated_at }}</p>
    </div>
    
    {% for section_name, section_data in sections.items() %}
    <div class="section">
        <h2>{{ section_data.title if section_data.title else section_name.replace('_', ' ').title() }}</h2>
        
        {% if section_data.content %}
            {% if section_data.content is string %}
                <p>{{ section_data.content }}</p>
            {% else %}
                {% for key, value in section_data.content.items() %}
                    {% if value is string or value is number %}
                        <p><strong>{{ key.replace('_', ' ').title() }}:</strong> {{ value }}</p>
                    {% elif value is iterable and value is not string %}
                        <p><strong>{{ key.replace('_', ' ').title() }}:</strong></p>
                        <ul>
                            {% for item in value[:10] %}
                                <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                {% endfor %}
            {% endif %}
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
            """

            # Render template
            template = Template(html_template)
            html_content = template.render(**content)

            # Write to file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"HTML report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"HTML generation failed: {str(e)}")
            raise

    async def _generate_excel_report(
        self,
        content: dict[str, Any],
        data_dict: dict[str, pd.DataFrame],
        base_filename: str,
    ) -> str:
        """Generate Excel report with multiple sheets"""
        try:
            filepath = os.path.join(self.output_directory, f"{base_filename}.xlsx")

            with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
                # Write data sheets
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name[:30], index=False)

                # Summary sheet
                summary_data = []
                for section_name, section_data in content["sections"].items():
                    if isinstance(section_data, dict) and "content" in section_data:
                        summary_data.append(
                            {
                                "Section": section_data.get("title", section_name),
                                "Content": (
                                    str(section_data["content"])[:100] + "..."
                                    if len(str(section_data["content"])) > 100
                                    else str(section_data["content"])
                                ),
                            }
                        )

                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name="Summary", index=False)

            logger.info(f"Excel report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Excel generation failed: {str(e)}")
            raise

    async def _generate_json_report(
        self, content: dict[str, Any], base_filename: str
    ) -> str:
        """Generate JSON report"""
        try:
            filepath = os.path.join(self.output_directory, f"{base_filename}.json")

            # Convert numpy types to native Python types for JSON serialization
            def convert_types(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {key: convert_types(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_types(item) for item in obj]
                else:
                    return obj

            converted_content = convert_types(content)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(converted_content, f, indent=2, default=str)

            logger.info(f"JSON report generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"JSON generation failed: {str(e)}")
            raise

    def _add_to_scheduler(self, scheduled_report: dict[str, Any]):
        """Add report to scheduler"""
        pattern = scheduled_report["schedule_pattern"]

        if pattern == "daily":
            schedule.every().day.at("09:00").do(
                self._execute_scheduled_report, scheduled_report["id"]
            )
        elif pattern == "weekly":
            schedule.every().monday.at("09:00").do(
                self._execute_scheduled_report, scheduled_report["id"]
            )
        elif pattern == "monthly":
            schedule.every().month.do(
                self._execute_scheduled_report, scheduled_report["id"]
            )
        else:
            logger.warning(f"Unsupported schedule pattern: {pattern}")

    def _execute_scheduled_report(self, schedule_id: str):
        """Execute scheduled report"""
        try:
            if schedule_id not in self.scheduled_reports:
                return

            report_config = self.scheduled_reports[schedule_id]

            # Get data
            data = report_config["data_source_func"]()

            # Generate report
            asyncio.run(self._run_scheduled_report(schedule_id, data))

        except Exception as e:
            logger.error(f"Scheduled report execution failed: {str(e)}")

    async def _run_scheduled_report(
        self, schedule_id: str, data: pd.DataFrame | dict[str, pd.DataFrame]
    ):
        """Run scheduled report generation"""
        report_config = self.scheduled_reports[schedule_id]

        # Generate report
        output_files = await self.generate_comprehensive_report(
            data_source=data,
            template_name=report_config["template_name"],
            report_title=report_config["name"],
            output_formats=report_config["output_formats"],
        )

        # Send email if configured
        if report_config["email_recipients"] and self.email_config:
            await self.send_report_email(
                recipients=report_config["email_recipients"],
                subject=f"Scheduled Report: {report_config['name']}",
                message=f"Please find attached the scheduled report: {report_config['name']}",
                attachments=list(output_files.values()),
            )

        # Update schedule tracking
        self.scheduled_reports[schedule_id]["last_run"] = datetime.now().isoformat()
        logger.info(f"Scheduled report executed: {report_config['name']}")

    def _run_scheduler(self):
        """Run the scheduler in background thread"""
        while self.is_scheduler_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


# Example usage and testing
if __name__ == "__main__":
    # Create sample data
    np.random.seed(42)

    sample_data = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=365, freq="D"),
            "sales": 10000 + np.cumsum(np.random.normal(100, 500, 365)),
            "customers": np.random.poisson(200, 365),
            "conversion_rate": np.random.beta(3, 7, 365),
            "product_category": np.random.choice(
                ["Electronics", "Clothing", "Books"], 365
            ),
            "region": np.random.choice(["North", "South", "East", "West"], 365),
        }
    )

    print("📋 Testing Automated Reporting System...")

    # Initialize reporting system
    reporting_system = AutomatedReportingSystem(output_directory="./test_reports")

    async def test_reporting():
        # Create custom template
        template = reporting_system.create_template(
            template_name="business_analytics",
            template_type="business_intelligence",
            sections=[
                "executive_summary",
                "key_metrics",
                "data_analysis",
                "insights",
                "recommendations",
            ],
        )

        # Generate comprehensive report
        output_files = await reporting_system.generate_comprehensive_report(
            data_source=sample_data,
            template_name="business_analytics",
            report_title="Business Analytics Report",
            output_formats=["pdf", "html", "excel", "json"],
            include_insights=True,
            include_predictions=True,
        )

        print(f"📊 Generated reports in {len(output_files)} formats:")
        for format_type, filepath in output_files.items():
            print(f"  • {format_type.upper()}: {filepath}")

        # Test report history
        history = reporting_system.get_report_history()
        print(f"📜 Report history contains {len(history)} entries")

        # Example of scheduled report (commented out to avoid actual scheduling)
        # def get_daily_data():
        #     return sample_data.tail(30)  # Last 30 days
        #
        # schedule_id = await reporting_system.schedule_report(
        #     report_name='Daily Business Summary',
        #     data_source_func=get_daily_data,
        #     schedule_pattern='daily',
        #     output_formats=['pdf', 'html']
        # )
        # print(f"⏰ Scheduled report with ID: {schedule_id}")

    asyncio.run(test_reporting())

    print("✅ Automated Reporting System test complete!")
