# State Management Guide

**Last Updated:** October 26, 2025  
**Library:** Zustand 4.x  
**Pattern:** Slice Pattern

## Table of Contents

- [Overview](#overview)
- [Store Structure](#store-structure)
- [Slice Pattern](#slice-pattern)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Advanced Patterns](#advanced-patterns)
- [Testing](#testing)

---

## Overview

We use **Zustand** for global state management because it's:

✅ **Simple** - No boilerplate, easy to learn  
✅ **Performant** - Only re-renders when subscribed state changes  
✅ **Type-Safe** - Full TypeScript support  
✅ **Flexible** - No providers, works anywhere  
✅ **DevTools** - Redux DevTools integration  

---

## Store Structure

```
store/
├── slices/              # State slices (one per domain)
│   ├── analytics.ts    # Analytics state & actions
│   ├── auth.ts         # Authentication state & actions
│   ├── channels.ts     # Channels state & actions
│   ├── media.ts        # Media upload state & actions
│   ├── posts.ts        # Posts state & actions
│   └── ui.ts           # UI state (sidebar, theme, etc.)
│
├── middleware/         # Custom middleware (optional)
│   └── logger.ts
│
└── index.ts            # Re-exports all slices
```

---

## Slice Pattern

### Basic Slice Structure

```typescript
// store/slices/example.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface ExampleState {
  // State
  data: Data | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchData: () => Promise<void>;
  updateData: (data: Data) => void;
  reset: () => void;
}

export const useExampleStore = create<ExampleState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        data: null,
        loading: false,
        error: null,
        
        // Actions
        fetchData: async () => {
          set({ loading: true, error: null });
          try {
            const data = await api.fetchData();
            set({ data, loading: false });
          } catch (error) {
            set({ error: error.message, loading: false });
          }
        },
        
        updateData: (data) => set({ data }),
        
        reset: () => set({
          data: null,
          loading: false,
          error: null,
        }),
      }),
      {
        name: 'example-storage', // localStorage key
      }
    )
  )
);
```

---

## Usage Examples

### 1. Auth Store

```typescript
// store/slices/auth.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { User } from '@/types';
import { apiClient } from '@api/client';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        
        login: async (email, password) => {
          set({ loading: true });
          try {
            const { user, token } = await apiClient.post('/auth/login', {
              email,
              password,
            });
            set({
              user,
              token,
              isAuthenticated: true,
              loading: false,
            });
          } catch (error) {
            set({ loading: false });
            throw error;
          }
        },
        
        logout: () => {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        },
        
        refreshUser: async () => {
          const { token } = get();
          if (!token) return;
          
          try {
            const user = await apiClient.get('/auth/me');
            set({ user });
          } catch (error) {
            get().logout();
          }
        },
        
        updateUser: (updates) => {
          set((state) => ({
            user: state.user ? { ...state.user, ...updates } : null,
          }));
        },
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          token: state.token,
          user: state.user,
        }),
      }
    ),
    { name: 'AuthStore' }
  )
);
```

**Usage in Components:**

```typescript
import { useAuthStore } from '@store';

function LoginForm() {
  const { login, loading, isAuthenticated } = useAuthStore();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      // Redirect on success
    } catch (error) {
      // Show error
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <button disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

function UserProfile() {
  const user = useAuthStore((state) => state.user);
  
  if (!user) return null;
  
  return <div>Welcome, {user.username}!</div>;
}
```

### 2. Analytics Store

```typescript
// store/slices/analytics.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { AnalyticsOverview, TimePeriod } from '@/types';

interface AnalyticsState {
  overview: AnalyticsOverview | null;
  period: TimePeriod;
  loading: boolean;
  error: string | null;
  
  fetchOverview: (period: TimePeriod) => Promise<void>;
  setPeriod: (period: TimePeriod) => void;
  reset: () => void;
}

export const useAnalyticsStore = create<AnalyticsState>()(
  devtools(
    (set, get) => ({
      overview: null,
      period: '7d',
      loading: false,
      error: null,
      
      fetchOverview: async (period) => {
        set({ loading: true, error: null });
        try {
          const overview = await analyticsService.getOverview(period);
          set({ overview, period, loading: false });
        } catch (error) {
          set({ error: error.message, loading: false });
        }
      },
      
      setPeriod: (period) => {
        set({ period });
        get().fetchOverview(period);
      },
      
      reset: () => set({
        overview: null,
        period: '7d',
        loading: false,
        error: null,
      }),
    }),
    { name: 'AnalyticsStore' }
  )
);
```

**Usage:**

```typescript
import { useAnalyticsStore } from '@store';

function AnalyticsDashboard() {
  const { overview, period, loading, setPeriod } = useAnalyticsStore();
  
  useEffect(() => {
    fetchOverview(period);
  }, []);
  
  return (
    <div>
      <PeriodSelector value={period} onChange={setPeriod} />
      {loading ? <Loading /> : <MetricsDisplay data={overview} />}
    </div>
  );
}
```

### 3. UI Store

```typescript
// store/slices/ui.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      theme: 'light',
      
      toggleSidebar: () => set((state) => ({
        sidebarCollapsed: !state.sidebarCollapsed,
      })),
      
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'ui-preferences',
    }
  )
);
```

---

## Best Practices

### 1. Keep Slices Small and Focused

✅ **Good:** One slice per domain
```typescript
useAuthStore      // Authentication only
useChannelStore   // Channels only
usePostStore      // Posts only
```

❌ **Bad:** One giant store
```typescript
useAppStore       // Everything mixed together
```

### 2. Co-locate Actions with State

✅ **Good:**
```typescript
export const useAuthStore = create<AuthState>()((set) => ({
  user: null,
  login: async (email, password) => { /* ... */ },
  logout: () => { /* ... */ },
}));
```

❌ **Bad:**
```typescript
// Separate files for state and actions
export const authState = { user: null };
export const authActions = { login, logout };
```

### 3. Use Selectors for Performance

✅ **Good:** Only subscribe to what you need
```typescript
const user = useAuthStore((state) => state.user);
const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
```

❌ **Bad:** Subscribe to entire store
```typescript
const { user, isAuthenticated, login, logout, ... } = useAuthStore();
```

### 4. Delegate Business Logic to Services

✅ **Good:**
```typescript
login: async (email, password) => {
  set({ loading: true });
  const { user, token } = await authService.login(email, password);
  set({ user, token, loading: false });
}
```

❌ **Bad:**
```typescript
login: async (email, password) => {
  // Complex business logic in store
  const hashedPassword = await bcrypt.hash(password);
  const response = await fetch('/api/login', { ... });
  // ... 50 more lines
}
```

### 5. Use TypeScript

✅ **Good:**
```typescript
interface AuthState {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>()(/*...*/);
```

### 6. Reset State on Logout

```typescript
logout: () => {
  set({
    user: null,
    token: null,
    isAuthenticated: false,
  });
  
  // Reset other stores if needed
  useChannelStore.getState().reset();
  usePostStore.getState().reset();
}
```

---

## Advanced Patterns

### 1. Derived State

Use selectors for computed values:

```typescript
const useChannelStore = create<ChannelState>()((set) => ({
  channels: [],
  selectedId: null,
  
  // Getter for derived state
  get selectedChannel() {
    const { channels, selectedId } = get();
    return channels.find((c) => c.id === selectedId);
  },
}));

// Usage
const selectedChannel = useChannelStore((state) => state.selectedChannel);
```

### 2. Async Actions with Error Handling

```typescript
fetchData: async () => {
  set({ loading: true, error: null });
  
  try {
    const data = await api.fetchData();
    set({ data, loading: false });
  } catch (error) {
    set({
      error: error instanceof Error ? error.message : 'An error occurred',
      loading: false,
    });
    
    // Optional: Show toast notification
    toast.error('Failed to fetch data');
  }
}
```

### 3. Middleware

**Logger Middleware:**

```typescript
import { StateCreator, StoreMutatorIdentifier } from 'zustand';

type Logger = <
  T extends object,
  Mps extends [StoreMutatorIdentifier, unknown][] = [],
  Mcs extends [StoreMutatorIdentifier, unknown][] = []
>(
  f: StateCreator<T, Mps, Mcs>,
  name?: string
) => StateCreator<T, Mps, Mcs>;

const logger: Logger = (f, name) => (set, get, store) => {
  const loggedSet: typeof set = (...args) => {
    console.log(`[${name}] State before:`, get());
    set(...args);
    console.log(`[${name}] State after:`, get());
  };
  return f(loggedSet, get, store);
};

// Usage
export const useAuthStore = create<AuthState>()(
  logger(
    (set) => ({
      user: null,
      login: async (email, password) => { /* ... */ },
    }),
    'AuthStore'
  )
);
```

### 4. Persistence with Migrations

```typescript
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({ /* ... */ }),
    {
      name: 'auth-storage',
      version: 2,
      migrate: (persistedState: any, version: number) => {
        // Migrate from v1 to v2
        if (version === 1) {
          return {
            ...persistedState,
            newField: 'default value',
          };
        }
        return persistedState;
      },
    }
  )
);
```

### 5. Subscriptions

Listen to store changes outside React:

```typescript
const unsubscribe = useAuthStore.subscribe(
  (state) => state.user,
  (user) => {
    console.log('User changed:', user);
  }
);

// Later
unsubscribe();
```

---

## Testing

### Testing Stores

```typescript
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '@store';

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  });
  
  it('should login user', async () => {
    const { result } = renderHook(() => useAuthStore());
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toBeTruthy();
  });
  
  it('should logout user', () => {
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});
```

### Testing Components with Store

```typescript
import { render, screen } from '@testing-library/react';
import { useAuthStore } from '@store';
import UserProfile from './UserProfile';

describe('UserProfile', () => {
  it('should display user info', () => {
    useAuthStore.setState({
      user: { id: 1, username: 'testuser' },
      isAuthenticated: true,
    });
    
    render(<UserProfile />);
    
    expect(screen.getByText('Welcome, testuser!')).toBeInTheDocument();
  });
});
```

---

## Store Index

All stores are exported from `store/index.ts`:

```typescript
// store/index.ts
export { useAuthStore } from './slices/auth';
export { useAnalyticsStore } from './slices/analytics';
export { useChannelStore } from './slices/channels';
export { useMediaStore } from './slices/media';
export { usePostStore } from './slices/posts';
export { useUIStore } from './slices/ui';

// Export types
export type * from './slices/auth';
export type * from './slices/analytics';
export type * from './slices/channels';
export type * from './slices/media';
export type * from './slices/posts';
export type * from './slices/ui';
```

**Usage:**

```typescript
import { useAuthStore, useAnalyticsStore } from '@store';
```

---

## Related Documentation

- [Architecture](./ARCHITECTURE.md) - Overall architecture
- [Import Guidelines](./IMPORT_GUIDELINES.md) - Import best practices
- [Zustand Documentation](https://docs.pmnd.rs/zustand) - Official docs

---

**Questions?** See the Zustand docs or ask the team!
