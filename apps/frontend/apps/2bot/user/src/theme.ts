import { createTheme } from '@mui/material/styles';

// Enhanced theme with improved accessibility and color contrast
const theme = createTheme({
  // Standardized spacing system
  spacing: 8, // Base unit: 8px

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
    // Paper component styling
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none'
        }
      }
    }
  },
});

export default theme;
