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
        }
      }
    },

    input: {
      sizes: {
        small: { height: 36, fontSize: '0.875rem' },
        medium: { height: 44, fontSize: '1rem' },
        large: { height: 52, fontSize: '1.125rem' }
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

  // Layout and spacing standards
  layout: {
    maxWidth: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px'
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

// Helper functions for consistent usage
export const getButtonProps = (size = 'medium', variant = 'primary') => ({
  ...DESIGN_TOKENS.components.button.sizes[size],
  ...DESIGN_TOKENS.components.button.variants[variant]
});

export const getCardProps = (variant = 'default') => ({
  ...DESIGN_TOKENS.components.card.variants[variant]
});

export const getStatusColor = (status) => {
  return DESIGN_TOKENS.status[status] || DESIGN_TOKENS.status.info;
};

export const getChartColors = (type = 'primary') => {
  return DESIGN_TOKENS.charts[type] || DESIGN_TOKENS.charts.primary;
};

// CSS-in-JS utility functions
export const createTransition = (property = 'all', duration = 'normal') => ({
  transition: `${property} ${DESIGN_TOKENS.animation.duration[duration]} ${DESIGN_TOKENS.animation.easing.ease}`
});

export const createElevation = (level = 1) => {
  const shadows = {
    1: '0 1px 3px rgba(0, 0, 0, 0.1)',
    2: '0 2px 8px rgba(0, 0, 0, 0.08)',
    4: '0 4px 12px rgba(0, 0, 0, 0.1)',
    6: '0 8px 24px rgba(0, 0, 0, 0.12)'
  };
  return { boxShadow: shadows[level] || shadows[1] };
};

export default DESIGN_TOKENS;