/**
 * Centralized Design Tokens
 *
 * This file establishes consistent design patterns across the entire application.
 * All components should reference these tokens instead of hardcoded values.
 */

// Base design tokens
export const DESIGN_TOKENS = {
  // Typography scale with consistent hierarchy
  typography: {
    scale: {
      xs: '0.75rem',   // 12px - captions, labels
      sm: '0.875rem',  // 14px - body text, descriptions
      base: '1rem',    // 16px - default body text
      lg: '1.125rem',  // 18px - subheadings
      xl: '1.25rem',   // 20px - headings
      '2xl': '1.5rem', // 24px - section titles
      '3xl': '2rem',   // 32px - page titles
      '4xl': '2.5rem'  // 40px - hero titles
    },
    weights: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    }
  },

  // Color system with consistent palette
  colors: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff'
    },
    background: {
      primary: '#ffffff',
      secondary: '#f8f9fa',
      tertiary: '#f1f3f4',
      paper: '#ffffff',
      default: '#fafbfc'
    },
    text: {
      primary: '#1c2128',
      secondary: '#656d76',
      disabled: '#8b949e',
      hint: '#656d76'
    },
    border: {
      default: '#d0d7de',
      muted: '#f1f3f4',
      subtle: '#eaeef2'
    },
    focus: {
      ring: '#1976d2',
      background: 'rgba(25, 118, 210, 0.08)'
    }
  },

  // Shape system for consistent styling
  shape: {
    borderRadius: {
      none: '0px',
      sm: '4px',
      md: '8px',
      lg: '12px',
      xl: '16px',
      '2xl': '24px',
      full: '9999px'
    }
  },

  // Elevation system for shadows and depth
  elevation: {
    none: '0',
    low: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
    medium: '0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23)',
    high: '0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23)',
    higher: '0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22)',
    highest: '0 19px 38px rgba(0, 0, 0, 0.30), 0 15px 12px rgba(0, 0, 0, 0.22)'
  },

  // Component sizing standards
  components: {
    button: {
      sizes: {
        small: { height: 32, padding: '6px 16px', fontSize: '0.875rem' },
        medium: { height: 40, padding: '8px 20px', fontSize: '1rem' },
        large: { height: 48, padding: '12px 24px', fontSize: '1.125rem' }
      },
      variants: {
        primary: { variant: 'contained', color: 'primary' },
        secondary: { variant: 'outlined', color: 'primary' },
        tertiary: { variant: 'text', color: 'primary' },
        danger: { variant: 'contained', color: 'error' },
        success: { variant: 'contained', color: 'success' }
      }
    },

    input: {
      sizes: {
        small: { height: 32, fontSize: '0.875rem', padding: '6px 12px' },
        medium: { height: 40, fontSize: '1rem', padding: '8px 16px' },
        large: { height: 48, fontSize: '1.125rem', padding: '12px 20px' }
      }
    },

    card: {
      variants: {
        default: {
          elevation: 1,
          borderRadius: 12,
          padding: '16px'
        },
        elevated: {
          elevation: 4,
          borderRadius: 12,
          padding: '20px',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        },
        interactive: {
          elevation: 2,
          borderRadius: 12,
          padding: '16px',
          cursor: 'pointer',
          '&:hover': { elevation: 6, transform: 'translateY(-2px)' }
        },
        outlined: {
          elevation: 0,
          borderRadius: 12,
          padding: '16px',
          border: '1px solid rgba(0, 0, 0, 0.12)'
        },
        filled: {
          elevation: 0,
          borderRadius: 12,
          padding: '16px',
          backgroundColor: 'rgba(0, 0, 0, 0.04)'
        }
      }
    },

    icon: {
      sizes: {
        xs: 16,
        sm: 20,
        md: 24,
        lg: 32,
        xl: 40
      }
    }
  },

  // Spacing system for consistent layouts
  spacing: {
    section: {
      padding: {
        xs: '16px',
        sm: '24px',
        md: '32px',
        lg: '48px',
        xl: '64px'
      },
      margin: {
        xs: '8px',
        sm: '16px',
        md: '24px',
        lg: '32px',
        xl: '48px'
      },
      gap: {
        xs: '8px',
        sm: '16px',
        md: '24px',
        lg: '32px',
        xl: '48px'
      }
    },
    component: {
      padding: {
        xs: '8px',
        sm: '12px',
        md: '16px',
        lg: '20px',
        xl: '24px'
      },
      gap: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px'
      }
    }
  },

  // Layout and spacing standards
  layout: {
    maxWidth: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px'
    },

    borderRadius: {
      none: '0px',
      sm: '4px',
      md: '8px',
      lg: '12px',
      xl: '16px',
      '2xl': '24px',
      full: '9999px'
    },

    container: {
      padding: {
        xs: '16px',
        sm: '24px',
        md: '32px'
      }
    },

    grid: {
      gap: {
        xs: 2,  // 16px
        sm: 3,  // 24px
        md: 4   // 32px
      }
    }
  },

  // Animation and transition standards
  animation: {
    duration: {
      fast: '150ms',
      normal: '250ms',
      slow: '400ms'
    },

    easing: {
      ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)'
    }
  },

  // Status and feedback colors
  status: {
    success: {
      main: '#3fb950',
      background: 'rgba(63, 185, 80, 0.1)',
      border: 'rgba(63, 185, 80, 0.3)'
    },
    warning: {
      main: '#f2cc60',
      background: 'rgba(242, 204, 96, 0.1)',
      border: 'rgba(242, 204, 96, 0.3)'
    },
    error: {
      main: '#f85149',
      background: 'rgba(248, 81, 73, 0.1)',
      border: 'rgba(248, 81, 73, 0.3)'
    },
    info: {
      main: '#58a6ff',
      background: 'rgba(88, 166, 255, 0.1)',
      border: 'rgba(88, 166, 255, 0.3)'
    }
  },

  // Data visualization colors
  charts: {
    primary: ['#58a6ff', '#79c0ff', '#a5f3fc', '#c7d2fe'],
    secondary: ['#f85149', '#ff7b7b', '#fca5a5', '#fecaca'],
    neutral: ['#8b949e', '#b1bac4', '#d0d7de', '#f0f6fc'],
    gradient: {
      primary: 'linear-gradient(135deg, #58a6ff 0%, #79c0ff 100%)',
      secondary: 'linear-gradient(135deg, #f85149 0%, #ff7b7b 100%)',
      success: 'linear-gradient(135deg, #3fb950 0%, #56d364 100%)'
    }
  }
};

type ButtonSize = 'small' | 'medium' | 'large';
type ButtonVariant = 'primary' | 'secondary' | 'tertiary' | 'danger' | 'success';
type CardVariant = 'default' | 'elevated' | 'interactive' | 'outlined' | 'filled';
type StatusType = 'success' | 'warning' | 'error' | 'info';
type ChartType = 'primary' | 'secondary' | 'neutral' | 'gradient';

// Helper functions for consistent usage
export const getButtonProps = (size: ButtonSize = 'medium', variant: ButtonVariant = 'primary') => ({
  ...DESIGN_TOKENS.components.button.sizes[size],
  ...DESIGN_TOKENS.components.button.variants[variant]
});

export const getCardProps = (variant: CardVariant = 'default') => ({
  ...DESIGN_TOKENS.components.card.variants[variant]
});

export const getStatusColor = (status: StatusType) => {
  return DESIGN_TOKENS.status[status] || DESIGN_TOKENS.status.info;
};

export const getChartColors = (type: ChartType = 'primary') => {
  return DESIGN_TOKENS.charts[type] || DESIGN_TOKENS.charts.primary;
};

type TransitionDuration = 'fast' | 'normal' | 'slow';

// CSS-in-JS utility functions
export const createTransition = (property: string = 'all', duration: TransitionDuration = 'normal') => ({
  transition: `${property} ${DESIGN_TOKENS.animation.duration[duration]} ${DESIGN_TOKENS.animation.easing.ease}`
});

export const createElevation = (level: 1 | 2 | 4 | 6 = 1) => {
  const shadows: Record<number, string> = {
    1: '0 1px 3px rgba(0, 0, 0, 0.1)',
    2: '0 2px 8px rgba(0, 0, 0, 0.08)',
    4: '0 4px 12px rgba(0, 0, 0, 0.1)',
    6: '0 8px 24px rgba(0, 0, 0, 0.12)'
  };
  return { boxShadow: shadows[level] || shadows[1] };
};

export default DESIGN_TOKENS;
