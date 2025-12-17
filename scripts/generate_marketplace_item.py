#!/usr/bin/env python3
"""
Marketplace Item Generator Script
Generates boilerplate files for new marketplace items (services, themes, widgets)

Usage:
    python scripts/generate_marketplace_item.py --type service --name "Anti Raid Protection" --key bot_anti_raid
    python scripts/generate_marketplace_item.py --type theme --name "Midnight Blue"
    python scripts/generate_marketplace_item.py --type widget --name "Engagement Tracker"
"""

import argparse
import re
from datetime import datetime
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "apps/frontend/apps/user/src"
BACKEND_SRC = PROJECT_ROOT / "apps"
CORE_SRC = PROJECT_ROOT / "core"


def to_snake_case(name: str) -> str:
    """Convert name to snake_case"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower().replace(" ", "_").replace("-", "_")


def to_pascal_case(name: str) -> str:
    """Convert name to PascalCase"""
    return "".join(word.capitalize() for word in name.replace("-", " ").replace("_", " ").split())


def to_kebab_case(name: str) -> str:
    """Convert name to kebab-case"""
    return to_snake_case(name).replace("_", "-")


def generate_service_config_component(name: str, service_key: str, category: str) -> str:
    """Generate React config component for a service"""
    pascal_name = to_pascal_case(name)

    return f"""/**
 * {name} Configuration
 * Service Key: {service_key}
 * Category: {category}
 * Generated: {datetime.now().strftime("%Y-%m-%d")}
 */

import React, {{ useEffect, useState }} from 'react';
import {{
  Box,
  Typography,
  Switch,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
}} from '@mui/material';
import {{
  Save as SaveIcon,
  // Add your service-specific icons here
}} from '@mui/icons-material';
import {{ apiClient }} from '@/api/client';

// TODO: Define your service settings interface
interface {pascal_name}Settings {{
  {to_snake_case(name)}_enabled: boolean;
  // Add your service-specific settings here
  // example_option: string;
  // example_number: number;
}}

interface Props {{
  chatId: number;
}}

export const {pascal_name}Config: React.FC<Props> = ({{ chatId }}) => {{
  const [settings, setSettings] = useState<{pascal_name}Settings>({{
    {to_snake_case(name)}_enabled: false,
    // Set defaults for your settings
  }});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {{
    const fetchSettings = async () => {{
      setIsLoading(true);
      try {{
        const response = await apiClient.get(`/bot/moderation/${{chatId}}/settings`) as {pascal_name}Settings;
        if (response) {{
          setSettings(prev => ({{
            ...prev,
            {to_snake_case(name)}_enabled: response.{to_snake_case(name)}_enabled ?? false,
            // Map other settings from response
          }}));
        }}
      }} catch (err: any) {{
        setError(err.message || 'Failed to load settings');
      }} finally {{
        setIsLoading(false);
      }}
    }};

    if (chatId) {{
      fetchSettings();
    }}
  }}, [chatId]);

  const handleSave = async () => {{
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {{
      await apiClient.patch(`/bot/moderation/${{chatId}}/settings`, settings);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    }} catch (err: any) {{
      setError(err.message || 'Failed to save settings');
    }} finally {{
      setIsSaving(false);
    }}
  }};

  if (isLoading) {{
    return (
      <Box display="flex" justifyContent="center" py={{4}}>
        <CircularProgress />
      </Box>
    );
  }}

  return (
    <Box>
      {{error && <Alert severity="error" sx={{{{ mb: 3 }}}}>{{error}}</Alert>}}
      {{success && <Alert severity="success" sx={{{{ mb: 3 }}}}>Settings saved successfully!</Alert>}}

      {{/* Main Toggle */}}
      <Card sx={{{{ mb: 3, bgcolor: alpha('#667eea', 0.05), border: '1px solid', borderColor: alpha('#667eea', 0.2) }}}}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={{2}}>
              {{/* TODO: Add your service icon here */}}
              <Box>
                <Typography variant="h6">{name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {{/* TODO: Add your service description */}}
                  Enable {name} for this chat
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={{settings.{to_snake_case(name)}_enabled}}
              onChange={{(e) => setSettings(prev => ({{ ...prev, {to_snake_case(name)}_enabled: e.target.checked }}))}}
              color="primary"
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {{settings.{to_snake_case(name)}_enabled && (
        <>
          <Divider sx={{{{ my: 3 }}}} />
          
          {{/* TODO: Add your service-specific configuration UI here */}}
          <Typography variant="subtitle1" mb={{2}}>
            Configuration Options
          </Typography>
          
          {{/* Example: Add sliders, selects, text fields for your settings */}}
        </>
      )}}

      {{/* Save Button */}}
      <Box mt={{4}} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={{isSaving ? <CircularProgress size={{20}} color="inherit" /> : <SaveIcon />}}
          onClick={{handleSave}}
          disabled={{isSaving}}
          size="large"
        >
          {{isSaving ? 'Saving...' : 'Save Settings'}}
        </Button>
      </Box>
    </Box>
  );
}};
"""


def generate_service_handler(name: str, service_key: str, category: str) -> str:
    """Generate Python handler for a service"""
    pascal_name = to_pascal_case(name)
    snake_name = to_snake_case(name)

    return f'''"""
{name} Service Handler
Service Key: {service_key}
Category: {category}
Generated: {datetime.now().strftime("%Y-%m-%d")}

This handler processes events for the {name} service.
"""

from typing import Optional, Any
from core.services.feature_gate_service import FeatureGateService
import logging

logger = logging.getLogger(__name__)


class {pascal_name}Handler:
    """
    Handler for {name} service
    
    This handler is responsible for:
    - Checking user access to the service
    - Processing events based on settings
    - Managing usage quotas (if applicable)
    """
    
    SERVICE_KEY = "{service_key}"
    
    def __init__(self, feature_gate: FeatureGateService):
        """
        Initialize the handler
        
        Args:
            feature_gate: Service for checking subscriptions and quotas
        """
        self.feature_gate = feature_gate
    
    async def check_access(self, user_id: int) -> bool:
        """
        Check if user has active subscription for this service
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user has access, False otherwise
        """
        try:
            return await self.feature_gate.check_subscription(
                user_id=user_id,
                service_key=self.SERVICE_KEY
            )
        except Exception as e:
            logger.error(f"Error checking access for {{user_id}}: {{e}}")
            return False
    
    async def get_settings(self, chat_id: int) -> Optional[dict]:
        """
        Get service settings for a chat
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Settings dictionary or None
        """
        # TODO: Implement settings retrieval from database
        # Example:
        # return await self.settings_repo.get_chat_settings(chat_id)
        pass
    
    async def process(
        self, 
        event: Any, 
        settings: dict,
        user_id: int
    ) -> bool:
        """
        Main processing logic for the service
        
        Args:
            event: Telegram event to process
            settings: Chat-specific settings for this service
            user_id: User ID who owns the subscription
            
        Returns:
            True if action was taken, False otherwise
        """
        # Check if service is enabled for this chat
        if not settings.get('{snake_name}_enabled', False):
            return False
        
        # Check user has active subscription
        if not await self.check_access(user_id):
            logger.debug(f"User {{user_id}} does not have access to {service_key}")
            return False
        
        # Check and consume quota if applicable
        # can_use = await self.feature_gate.check_and_consume_quota(
        #     user_id=user_id,
        #     service_key=self.SERVICE_KEY
        # )
        # if not can_use:
        #     logger.debug(f"User {{user_id}} exceeded quota for {service_key}")
        #     return False
        
        # TODO: Implement your service logic here
        # Example:
        # - Anti-spam: Check message for spam patterns
        # - Auto-delete: Delete system messages
        # - Welcome: Send welcome message to new members
        
        return False
    
    async def on_enable(self, chat_id: int, user_id: int) -> None:
        """
        Called when service is enabled for a chat
        
        Args:
            chat_id: Telegram chat ID
            user_id: User who enabled the service
        """
        logger.info(f"{name} enabled for chat {{chat_id}} by user {{user_id}}")
        # TODO: Any initialization logic
    
    async def on_disable(self, chat_id: int, user_id: int) -> None:
        """
        Called when service is disabled for a chat
        
        Args:
            chat_id: Telegram chat ID
            user_id: User who disabled the service
        """
        logger.info(f"{name} disabled for chat {{chat_id}} by user {{user_id}}")
        # TODO: Any cleanup logic
'''


def generate_service_seed(name: str, service_key: str, category: str, price: int) -> str:
    """Generate SQL seed for a service"""
    return f"""-- {name} Service Seed
-- Generated: {datetime.now().strftime("%Y-%m-%d")}

INSERT INTO marketplace_services (
    service_key,
    name,
    short_description,
    description,
    category,
    icon,
    color,
    price_credits_monthly,
    price_credits_yearly,
    features,
    is_active,
    is_featured,
    is_popular,
    sort_order,
    created_at,
    updated_at
) VALUES (
    '{service_key}',
    '{name}',
    'Short description of {name}',  -- TODO: Update this
    'Full description of {name} service with all details about what it does and how it helps users.',  -- TODO: Update this
    '{category}',
    'Extension',  -- TODO: Choose appropriate MUI icon name
    '#667eea',  -- TODO: Choose service color
    {price},  -- Monthly price in credits
    {int(price * 10)},  -- Yearly price (typically 10 months = 2 months free)
    '["Feature 1", "Feature 2", "Feature 3"]'::jsonb,  -- TODO: List actual features
    true,
    false,
    false,
    100,  -- TODO: Set appropriate sort order
    NOW(),
    NOW()
) ON CONFLICT (service_key) DO NOTHING;
"""


def generate_theme_files(name: str) -> tuple[str, str]:
    """Generate theme definition files"""
    to_pascal_case(name)
    kebab_name = to_kebab_case(name)

    theme_ts = f"""/**
 * {name} Theme
 * Generated: {datetime.now().strftime("%Y-%m-%d")}
 */

import {{ createTheme, ThemeOptions }} from '@mui/material/styles';

export const {to_snake_case(name)}ThemeOptions: ThemeOptions = {{
  palette: {{
    mode: 'dark',  // or 'light'
    primary: {{
      main: '#667eea',
      light: '#8b9ff0',
      dark: '#4a5bc4',
    }},
    secondary: {{
      main: '#764ba2',
      light: '#9a6fc4',
      dark: '#5a3580',
    }},
    background: {{
      default: '#0a0a0f',
      paper: '#12121a',
    }},
    text: {{
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    }},
    divider: 'rgba(255, 255, 255, 0.12)',
    // TODO: Customize colors for your theme
  }},
  typography: {{
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {{
      fontWeight: 600,
    }},
    h2: {{
      fontWeight: 600,
    }},
    h3: {{
      fontWeight: 600,
    }},
    // TODO: Customize typography
  }},
  shape: {{
    borderRadius: 8,
  }},
  components: {{
    MuiButton: {{
      styleOverrides: {{
        root: {{
          textTransform: 'none',
          borderRadius: 8,
        }},
      }},
    }},
    MuiCard: {{
      styleOverrides: {{
        root: {{
          borderRadius: 12,
        }},
      }},
    }},
    // TODO: Add component overrides for your theme
  }},
}};

export const {to_snake_case(name)}Theme = createTheme({to_snake_case(name)}ThemeOptions);

export const themeMetadata = {{
  id: 'theme_{to_snake_case(name)}',
  name: '{name}',
  description: 'A beautiful {name.lower()} theme for AnalyticBot',
  author: 'Developer Name',  // TODO: Update
  version: '1.0.0',
  previewImage: '/themes/{kebab_name}/preview.png',
  tags: ['dark', 'modern'],  // TODO: Update tags
}};

export default {to_snake_case(name)}Theme;
"""

    seed_sql = f"""-- {name} Theme Seed
-- Generated: {datetime.now().strftime("%Y-%m-%d")}

INSERT INTO marketplace_items (
    unique_key,
    name,
    slug,
    description,
    category,
    icon_url,
    preview_images,
    price_credits,
    version,
    is_active,
    is_featured,
    sort_order,
    created_at,
    updated_at
) VALUES (
    'theme_{to_snake_case(name)}',
    '{name}',
    '{kebab_name}',
    'A beautiful {name.lower()} theme that transforms your dashboard experience.',  -- TODO: Update
    'themes',
    '/themes/{kebab_name}/icon.png',
    '["/themes/{kebab_name}/preview.png"]'::jsonb,
    50,  -- TODO: Set price
    '1.0.0',
    true,
    false,
    100,
    NOW(),
    NOW()
) ON CONFLICT (unique_key) DO NOTHING;
"""

    return theme_ts, seed_sql


def generate_widget_files(name: str) -> tuple[str, str]:
    """Generate widget component and seed"""
    pascal_name = to_pascal_case(name)
    snake_name = to_snake_case(name)

    widget_tsx = f"""/**
 * {name} Widget
 * Generated: {datetime.now().strftime("%Y-%m-%d")}
 */

import React, {{ useEffect, useState }} from 'react';
import {{
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  CircularProgress,
  IconButton,
  Tooltip,
}} from '@mui/material';
import {{
  Refresh as RefreshIcon,
  // TODO: Add your widget-specific icons
}} from '@mui/icons-material';
import {{ apiClient }} from '@/api/client';

export interface {pascal_name}WidgetProps {{
  size: 'small' | 'medium' | 'large';
  refreshInterval?: number;  // in milliseconds
}}

interface WidgetData {{
  // TODO: Define your widget's data structure
  value: number;
  label: string;
}}

export const {pascal_name}Widget: React.FC<{pascal_name}WidgetProps> = ({{
  size = 'medium',
  refreshInterval = 60000,
}}) => {{
  const [data, setData] = useState<WidgetData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {{
    try {{
      setIsLoading(true);
      // TODO: Update API endpoint
      const response = await apiClient.get('/widgets/{snake_name}/data') as WidgetData;
      setData(response);
      setError(null);
    }} catch (err: any) {{
      setError(err.message || 'Failed to load data');
    }} finally {{
      setIsLoading(false);
    }}
  }};

  useEffect(() => {{
    fetchData();
    
    if (refreshInterval > 0) {{
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }}
  }}, [refreshInterval]);

  const getSizeStyles = () => {{
    switch (size) {{
      case 'small':
        return {{ minHeight: 120, minWidth: 150 }};
      case 'large':
        return {{ minHeight: 300, minWidth: 400 }};
      default:
        return {{ minHeight: 200, minWidth: 250 }};
    }}
  }};

  return (
    <Card sx={{{{ ...getSizeStyles() }}}}>
      <CardHeader
        title="{name}"
        titleTypographyProps={{{{ variant: size === 'small' ? 'body1' : 'h6' }}}}
        action={{
          <Tooltip title="Refresh">
            <IconButton onClick={{fetchData}} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        }}
        sx={{{{ pb: 0 }}}}
      />
      <CardContent>
        {{isLoading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="100%">
            <CircularProgress size={{24}} />
          </Box>
        ) : error ? (
          <Typography color="error" variant="body2">
            {{error}}
          </Typography>
        ) : data ? (
          <Box>
            {{/* TODO: Render your widget data */}}
            <Typography variant="h4">{{data.value}}</Typography>
            <Typography variant="body2" color="text.secondary">
              {{data.label}}
            </Typography>
          </Box>
        ) : null}}
      </CardContent>
    </Card>
  );
}};

// Widget metadata for registration
export const widgetMetadata = {{
  id: 'widget_{snake_name}',
  name: '{name}',
  description: 'Displays...',  // TODO: Update description
  sizes: ['small', 'medium', 'large'] as const,
  defaultSize: 'medium' as const,
  category: 'analytics',  // analytics | social | tools
  dataSource: '/widgets/{snake_name}/data',
  refreshable: true,
  configurable: false,  // Set true if widget has settings
}};

export default {pascal_name}Widget;
"""

    seed_sql = f"""-- {name} Widget Seed
-- Generated: {datetime.now().strftime("%Y-%m-%d")}

INSERT INTO marketplace_items (
    unique_key,
    name,
    slug,
    description,
    category,
    icon_url,
    preview_images,
    price_credits,
    version,
    is_active,
    is_featured,
    sort_order,
    created_at,
    updated_at
) VALUES (
    'widget_{snake_name}',
    '{name}',
    '{to_kebab_case(name)}',
    'A powerful widget that displays...',  -- TODO: Update
    'widgets',
    '/widgets/{to_kebab_case(name)}/icon.png',
    '["/widgets/{to_kebab_case(name)}/preview.png"]'::jsonb,
    30,  -- TODO: Set price
    '1.0.0',
    true,
    false,
    100,
    NOW(),
    NOW()
) ON CONFLICT (unique_key) DO NOTHING;
"""

    return widget_tsx, seed_sql


def main():
    parser = argparse.ArgumentParser(
        description="Generate marketplace item boilerplate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --type service --name "Anti Raid Protection" --key bot_anti_raid --category bot_service
  %(prog)s --type theme --name "Midnight Blue"
  %(prog)s --type widget --name "Engagement Tracker"
        """,
    )

    parser.add_argument(
        "--type",
        "-t",
        required=True,
        choices=["service", "theme", "widget"],
        help="Type of marketplace item to generate",
    )
    parser.add_argument("--name", "-n", required=True, help="Display name for the item")
    parser.add_argument(
        "--key",
        "-k",
        help="Service key (required for services, auto-generated otherwise)",
    )
    parser.add_argument(
        "--category",
        "-c",
        default="bot_service",
        choices=["bot_service", "mtproto_services", "ai_services"],
        help="Category for services (default: bot_service)",
    )
    parser.add_argument(
        "--price", "-p", type=int, default=100, help="Price in credits (default: 100)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./generated",
        help="Output directory (default: ./generated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be generated without writing files",
    )

    args = parser.parse_args()

    # Auto-generate key if not provided
    if not args.key:
        prefix = args.type if args.type != "service" else args.category.split("_")[0]
        args.key = f"{prefix}_{to_snake_case(args.name)}"

    output_dir = Path(args.output)
    files_to_create = []

    if args.type == "service":
        # Generate service files
        config_component = generate_service_config_component(args.name, args.key, args.category)
        handler = generate_service_handler(args.name, args.key, args.category)
        seed = generate_service_seed(args.name, args.key, args.category, args.price)

        pascal_name = to_pascal_case(args.name)
        files_to_create = [
            (
                output_dir / f"frontend/configs/{pascal_name}Config.tsx",
                config_component,
            ),
            (
                output_dir / f"backend/handlers/{to_snake_case(args.name)}_handler.py",
                handler,
            ),
            (output_dir / f"seeds/{args.key}_seed.sql", seed),
        ]

    elif args.type == "theme":
        theme_ts, seed_sql = generate_theme_files(args.name)
        kebab_name = to_kebab_case(args.name)

        files_to_create = [
            (output_dir / f"themes/{kebab_name}/index.ts", theme_ts),
            (output_dir / f"seeds/theme_{to_snake_case(args.name)}_seed.sql", seed_sql),
        ]

    elif args.type == "widget":
        widget_tsx, seed_sql = generate_widget_files(args.name)
        pascal_name = to_pascal_case(args.name)

        files_to_create = [
            (output_dir / f"widgets/{pascal_name}Widget.tsx", widget_tsx),
            (
                output_dir / f"seeds/widget_{to_snake_case(args.name)}_seed.sql",
                seed_sql,
            ),
        ]

    # Output results
    print(f"\n{'=' * 60}")
    print("  Marketplace Item Generator")
    print(f"{'=' * 60}")
    print(f"  Type: {args.type}")
    print(f"  Name: {args.name}")
    print(f"  Key:  {args.key}")
    if args.type == "service":
        print(f"  Category: {args.category}")
    print(f"  Price: {args.price} credits")
    print(f"{'=' * 60}\n")

    if args.dry_run:
        print("DRY RUN - Files that would be created:\n")
        for path, content in files_to_create:
            print(f"📄 {path}")
            print(f"   ({len(content)} bytes)\n")
    else:
        print("Creating files:\n")
        for path, content in files_to_create:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"✅ Created: {path}")

        print(f"\n{'=' * 60}")
        print("  Next Steps:")
        print(f"{'=' * 60}")
        print(
            """
1. Review and customize the generated files
2. Move files to their proper locations:
   - Frontend configs → apps/frontend/apps/user/src/pages/services/configs/
   - Backend handlers → apps/bot/handlers/services/
   - Seeds → Run in database

3. Register in the system:
   - Add to SERVICE_CONFIG_MAP in ServiceConfigPage.tsx
   - Add icon mapping in ActiveServicesCard.tsx
   - Add service details in SERVICE_DETAILS

4. Test the integration:
   - Purchase flow
   - Settings save/load
   - Service functionality

See docs/MARKETPLACE_DEVELOPER_GUIDE.md for full details.
"""
        )


if __name__ == "__main__":
    main()
