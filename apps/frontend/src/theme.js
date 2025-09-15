import { createTheme } from '@mui/material/styles';
import { SPACING_SCALE, SEMANTIC_SPACING } from './theme/spacingSystem.js';

// Enhanced theme with improved accessibility and color contrast
const theme = createTheme({
  // Standardized spacing system
  spacing: 8, // Base unit: 8px
  
  // Custom spacing scale for consistent design
  spacingScale: SPACING_SCALE,
  semanticSpacing: SEMANTIC_SPACING,
  palette: {
    mode: 'dark',
    primary: {
      main: '#58a6ff', // High contrast blue - 7:1 contrast ratio
      light: '#79c0ff',
      dark: '#388bfd',
      contrastText: '#ffffff'
    },
    secondary: {
      main: '#f85149', // High contrast red
      light: '#ff7b7b', 
      dark: '#da3633',
      contrastText: '#ffffff'
    },
    success: {
      main: '#3fb950', // Accessible green
      light: '#56d364',
      dark: '#238636',
      contrastText: '#ffffff'
    },
    warning: {
      main: '#f2cc60', // High contrast yellow
      light: '#ffdf5d',
      dark: '#e3b341',
      contrastText: '#000000'
    },
    error: {
      main: '#f85149', // High contrast red
      light: '#ff7b7b',
      dark: '#da3633', 
      contrastText: '#ffffff'
    },
    background: {
      default: '#0d1117', // Main background - adequate contrast
      paper: '#161b22',   // Card backgrounds - adequate contrast
    },
    text: {
      primary: '#f0f6fc',    // High contrast white text - 15:1 ratio
      secondary: '#8b949e',  // Medium contrast gray - 4.8:1 ratio
      disabled: '#484f58',   // Disabled text
    },
    divider: '#30363d',      // Subtle dividers
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h2: {
      fontSize: '1.5rem', 
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h3: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.25,
    },
    // Ensure adequate line spacing for readability
    body1: {
      lineHeight: 1.6,
    },
    body2: {
      lineHeight: 1.5,
    }
  },
  components: {
    // Enhanced focus indicators for accessibility
    MuiCssBaseline: {
      styleOverrides: {
        '*:focus-visible': {
          outline: '3px solid #58a6ff',
          outlineOffset: '2px',
          borderRadius: '3px',
        },
        // High contrast mode support
        '@media (prefers-contrast: high)': {
          '*:focus-visible': {
            outline: '3px solid #ffffff',
            outlineOffset: '2px',
          }
        },
        // Reduced motion support
        '@media (prefers-reduced-motion: reduce)': {
          '*': {
            animationDuration: '0.01ms !important',
            animationIterationCount: '1 !important',
            transitionDuration: '0.01ms !important',
          }
        }
      }
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            minHeight: '44px',
            '& fieldset': {
              borderColor: '#30363d',
              borderWidth: '1px',
            },
            '&:hover fieldset': {
              borderColor: '#58a6ff',
              borderWidth: '2px',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#58a6ff',
              borderWidth: '2px',
              boxShadow: '0 0 0 3px rgba(88, 166, 255, 0.1)',
            },
            '&.Mui-error fieldset': {
              borderColor: '#f85149',
              borderWidth: '2px',
            },
            '&.Mui-error:hover fieldset': {
              borderColor: '#ff7b7b',
            },
            '&.MuiInputBase-sizeSmall': {
              minHeight: '36px',
              '@media (hover: none)': {
                minHeight: '44px',
              }
            }
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '6px',
          fontWeight: 500,
          padding: '8px 16px',
          minHeight: '44px', // Minimum touch target size
          '&:focus-visible': {
            outline: '3px solid #58a6ff',
            outlineOffset: '2px',
          },
          '&.Mui-disabled': {
            opacity: 0.6,
            cursor: 'not-allowed',
          }
        },
        contained: {
          boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
          '&:hover': {
            boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
          }
        }
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          minWidth: '44px',  // Minimum touch target size
          minHeight: '44px',
          padding: '10px',
          '&:focus-visible': {
            outline: '3px solid #58a6ff',
            outlineOffset: '2px',
          },
          // Ensure small buttons have adequate touch area on mobile
          '&.MuiIconButton-sizeSmall': {
            minWidth: '36px',
            minHeight: '36px',
            padding: '6px',
            '@media (hover: none)': {
              minWidth: '44px',
              minHeight: '44px',
              padding: '10px',
            }
          }
        }
      }
    },
    MuiChip: {
      styleOverrides: {
        root: {
          minHeight: '32px',
          '&:focus-visible': {
            outline: '3px solid #58a6ff',
            outlineOffset: '2px',
          },
          // Clickable chips need larger touch targets
          '&.MuiChip-clickable, &.MuiChip-deletable': {
            minHeight: '36px',
            '@media (hover: none)': {
              minHeight: '44px',
            }
          }
        }
      }
    },
    MuiTab: {
      styleOverrides: {
        root: {
          minHeight: '48px',  // Adequate touch target
          padding: '12px 16px',
          '&:focus-visible': {
            outline: '3px solid #58a6ff',
            outlineOffset: '2px',
          },
          // Ensure tabs are always touch-friendly
          '@media (hover: none)': {
            minHeight: '56px',
            padding: '16px 20px',
          }
        }
      }
    },
    // Enhanced table accessibility
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: '#30363d',
          '&.MuiTableCell-head': {
            fontWeight: 600,
            backgroundColor: '#161b22',
          }
        }
      }
    },
    // Enhanced alert styling
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: '6px',
          '& .MuiAlert-icon': {
            alignSelf: 'flex-start',
            marginTop: '2px',
          }
        }
      }
    },
    // Form controls with touch targets
    MuiFormControl: {
      styleOverrides: {
        root: {
          '& .MuiSelect-select': {
            minHeight: '20px',
            padding: '10px 14px',
          },
          '&.MuiFormControl-sizeSmall .MuiSelect-select': {
            minHeight: '16px',
            padding: '8px 14px',
            '@media (hover: none)': {
              minHeight: '20px',
              padding: '10px 14px',
            }
          }
        }
      }
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          minHeight: '44px',
          '&.MuiInputBase-sizeSmall': {
            minHeight: '36px',
            '@media (hover: none)': {
              minHeight: '44px',
            }
          },
          '&:focus-visible': {
            outline: '3px solid #58a6ff',
            outlineOffset: '2px',
          }
        }
      }
    },
    // Menu items with adequate spacing
    MuiMenuItem: {
      styleOverrides: {
        root: {
          minHeight: '44px',
          padding: '8px 16px',
          '&:focus-visible': {
            outline: '2px solid #58a6ff',
            outlineOffset: '-2px',
          }
        }
      }
    },
    // Common layout patterns as theme variants
    MuiContainer: {
      variants: [
        {
          props: { variant: 'dashboard' },
          style: {
            maxWidth: 'xl',
            py: 3,
            minHeight: '100vh'
          }
        },
        {
          props: { variant: 'page' },
          style: {
            maxWidth: 'sm',
            py: 4
          }
        }
      ]
    },
    MuiPaper: {
      variants: [
        {
          props: { variant: 'card' },
          style: {
            padding: '24px',
            borderRadius: '8px',
            marginBottom: '32px'
          }
        },
        {
          props: { variant: 'chart' },
          style: {
            padding: '16px',
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider'
          }
        },
        {
          props: { variant: 'legend' },
          style: {
            padding: '16px',
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: '4px'
          }
        }
      ],
      styleOverrides: {
        root: {
          backgroundImage: 'none'
        }
      }
    },
    MuiBox: {
      variants: [
        {
          props: { variant: 'flexCenter' },
          style: {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
          }
        },
        {
          props: { variant: 'flexBetween' },
          style: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }
        },
        {
          props: { variant: 'flexColumn' },
          style: {
            display: 'flex',
            flexDirection: 'column'
          }
        },
        {
          props: { variant: 'flexRow' },
          style: {
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }
        },
        {
          props: { variant: 'chartContainer' },
          style: {
            height: '400px',
            marginTop: '16px'
          }
        },
        {
          props: { variant: 'emptyState' },
          style: {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '400px',
            flexDirection: 'column'
          }
        },
        {
          props: { variant: 'headerControls' },
          style: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '24px'
          }
        },
        {
          props: { variant: 'actionControls' },
          style: {
            display: 'flex',
            gap: '16px'
          }
        },
        {
          props: { variant: 'chipGroup' },
          style: {
            display: 'flex',
            gap: '8px'
          }
        },
        {
          props: { variant: 'responsiveGrid' },
          style: {
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              md: '2fr 1fr'
            },
            gap: '24px'
          }
        },
        {
          props: { variant: 'tabContent' },
          style: {
            padding: '24px'
          }
        },
        {
          props: { variant: 'borderBox' },
          style: {
            display: 'flex',
            borderBottom: '1px solid #e0e0e0'
          }
        },
        {
          props: { variant: 'centeredText' },
          style: {
            textAlign: 'center'
          }
        },
        {
          props: { variant: 'iconText' },
          style: {
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '8px'
          }
        },
        {
          props: { variant: 'responsiveGridLg' },
          style: {
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              lg: '1fr 1fr'
            },
            gap: '24px'
          }
        },
        {
          props: { variant: 'statusFooter' },
          style: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: '16px',
            paddingTop: '16px',
            borderTop: '1px solid',
            borderColor: 'divider'
          }
        },
        {
          props: { variant: 'mainLayout' },
          style: {
            display: 'flex',
            minHeight: 'calc(100vh - 64px)'
          }
        },
        {
          props: { variant: 'mainContent' },
          style: {
            flexGrow: 1,
            backgroundColor: 'background.default',
            minHeight: 'calc(100vh - 64px)',
            padding: '24px'
          }
        },
        {
          props: { variant: 'drawerContent' },
          style: {
            padding: '16px'
          }
        }
      ]
    },
    // Card variants for different layouts
    MuiCard: {
      variants: [
        {
          props: { variant: 'metric' },
          style: {
            textAlign: 'center',
            padding: '16px'
          }
        },
        {
          props: { variant: 'service' },
          style: {
            padding: '24px'
          }
        }
      ]
    },
    MuiCardContent: {
      variants: [
        {
          props: { variant: 'metric' },
          style: {
            padding: '16px',
            '&:last-child': {
              paddingBottom: '16px'
            }
          }
        },
        {
          props: { variant: 'service' },
          style: {
            padding: '24px'
          }
        }
      ]
    },
    MuiFormControl: {
      variants: [
        {
          props: { variant: 'compact' },
          style: {
            minWidth: '120px'
          }
        }
      ],
      styleOverrides: {
        root: {
          '& .MuiSelect-select': {
            minHeight: '20px',
            padding: '10px 14px',
          },
          '&.MuiFormControl-sizeSmall .MuiSelect-select': {
            minHeight: '16px',
            padding: '8px 14px',
            '@media (hover: none)': {
              minHeight: '20px',
              padding: '10px 14px',
            }
          }
        }
      }
    },
    MuiAlert: {
      variants: [
        {
          props: { variant: 'spaced' },
          style: {
            margin: '16px'
          }
        },
        {
          props: { variant: 'topSpaced' },
          style: {
            marginTop: '24px'
          }
        },
        {
          props: { variant: 'bottomSpaced' },
          style: {
            marginBottom: '16px'
          }
        }
      ],
      styleOverrides: {
        root: {
          borderRadius: '6px',
          '& .MuiAlert-icon': {
            alignSelf: 'flex-start',
            marginTop: '2px',
          }
        }
      }
    },
    MuiTypography: {
      variants: [
        {
          props: { variant: 'pageTitle' },
          style: {
            marginBottom: '16px',
            fontWeight: 600
          }
        },
        {
          props: { variant: 'sectionTitle' },
          style: {
            marginBottom: '8px'
          }
        },
        {
          props: { variant: 'withIcon' },
          style: {
            marginLeft: '16px'
          }
        }
      ]
    },
    MuiGrid: {
      variants: [
        {
          props: { variant: 'metricsGrid' },
          style: {
            marginBottom: '24px'
          }
        }
      ]
    },
    MuiSkeleton: {
      variants: [
        {
          props: { variant: 'centered' },
          style: {
            marginLeft: 'auto',
            marginRight: 'auto'
          }
        },
        {
          props: { variant: 'centeredWithMargin' },
          style: {
            marginLeft: 'auto',
            marginRight: 'auto',
            marginTop: '8px'
          }
        }
      ]
    },
    // Stack component variants for common spacing patterns
    MuiStack: {
      variants: [
        {
          props: { variant: 'page' },
          style: {
            spacing: 3,
            marginTop: '16px'
          }
        },
        {
          props: { variant: 'wrapped' },
          style: {
            flexWrap: 'wrap',
            gap: '8px'
          }
        }
      ]
    },
    // Tab component variants
    MuiTabs: {
      variants: [
        {
          props: { variant: 'bordered' },
          style: {
            borderBottom: '1px solid',
            borderColor: 'divider',
            paddingLeft: '16px',
            paddingRight: '16px'
          }
        }
      ]
    },
    // FormControl component variants
    MuiFormControl: {
      variants: [
        {
          props: { variant: 'compact' },
          style: {
            minWidth: 120,
            '& .MuiSelect-select': {
              padding: '8px 14px'
            }
          }
        },
        {
          props: { variant: 'inline' },
          style: {
            minWidth: 150,
            marginRight: '16px'
          }
        }
      ]
    },
    // Typography variants for sections
    MuiTypography: {
      variants: [
        {
          props: { variant: 'navHeader' },
          style: {
            marginBottom: '16px',
            fontWeight: 600,
            color: 'text.secondary'
          }
        }
      ]
    },
    // Drawer variants for navigation layouts
    MuiDrawer: {
      variants: [
        {
          props: { variant: 'servicesNav' },
          style: {
            width: 280,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 280,
              boxSizing: 'border-box',
              borderRight: '1px solid',
              borderColor: 'divider',
              position: 'relative',
              height: 'calc(100vh - 64px)',
              overflow: 'auto'
            }
          }
        }
      ]
    },
    // ListItemButton variants for navigation
    MuiListItemButton: {
      variants: [
        {
          props: { variant: 'navigation' },
          style: {
            minHeight: 56,
            borderRadius: 8,
            '&.Mui-selected': {
              backgroundColor: 'primary.main',
              color: 'primary.contrastText',
              '& .MuiListItemIcon-root': {
                color: 'inherit'
              },
              '&:hover': {
                backgroundColor: 'primary.dark'
              }
            }
          }
        }
      ]
    },
    // ListItem variants for navigation lists
    MuiListItem: {
      variants: [
        {
          props: { variant: 'navigation' },
          style: {
            marginBottom: '8px'
          }
        }
      ]
    },
    // ListItemIcon variants for compact layouts
    MuiListItemIcon: {
      variants: [
        {
          props: { variant: 'compact' },
          style: {
            minWidth: 40
          }
        }
      ]
    },
    // Chip variants for status indicators
    MuiChip: {
      variants: [
        {
          props: { variant: 'status' },
          style: {
            fontSize: '0.7rem',
            height: 20,
            '& .MuiChip-label': {
              paddingLeft: 8,
              paddingRight: 8
            }
          }
        }
      ]
    },
    // Common icon patterns
    MuiSvgIcon: {
      variants: [
        {
          props: { variant: 'large' },
          style: {
            fontSize: 64,
            marginBottom: '16px',
            opacity: 0.5
          }
        },
        {
          props: { variant: 'header' },
          style: {
            fontSize: 32,
            color: 'primary.main'
          }
        }
      ]
    }
  },
});

export default theme;
