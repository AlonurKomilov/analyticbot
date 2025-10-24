/**
 * Telegram Login Widget Integration
 * 
 * This file shows how to add "Sign in with Telegram" to your React login page.
 * Works with the backend API we just created.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// ============================================================================
// Configuration
// ============================================================================

const TELEGRAM_BOT_USERNAME = process.env.REACT_APP_TELEGRAM_BOT_USERNAME || 'YourAnalyticBot';
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// ============================================================================
// Telegram Widget Component (Option 1 - Recommended)
// ============================================================================

export const TelegramLoginWidget = ({ onAuth }) => {
  useEffect(() => {
    // Dynamically load Telegram widget script
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.async = true;
    script.setAttribute('data-telegram-login', TELEGRAM_BOT_USERNAME);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-onauth', 'onTelegramAuth(user)');
    script.setAttribute('data-request-access', 'write');

    // Create callback function
    window.onTelegramAuth = (user) => {
      console.log('Telegram auth received:', user);
      handleTelegramAuth(user);
    };

    const widgetContainer = document.getElementById('telegram-widget-container');
    if (widgetContainer) {
      widgetContainer.appendChild(script);
    }

    return () => {
      // Cleanup
      if (widgetContainer && script.parentNode) {
        widgetContainer.removeChild(script);
      }
      delete window.onTelegramAuth;
    };
  }, []);

  const handleTelegramAuth = async (user) => {
    try {
      // Send Telegram data to your backend
      const response = await fetch(`${API_BASE_URL}/api/auth/telegram/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(user),
      });

      if (!response.ok) {
        throw new Error('Telegram authentication failed');
      }

      const data = await response.json();

      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Call parent callback
      if (onAuth) {
        onAuth(data);
      }
    } catch (error) {
      console.error('Telegram auth error:', error);
      alert('Failed to sign in with Telegram. Please try again.');
    }
  };

  return (
    <div 
      id="telegram-widget-container"
      className="telegram-login-widget"
      style={{ marginTop: '20px' }}
    />
  );
};

// ============================================================================
// Manual Button Component (Option 2 - More Control)
// ============================================================================

export const TelegramLoginButton = ({ onAuth }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = () => {
    setIsLoading(true);

    // Open Telegram OAuth URL
    const authUrl = `https://oauth.telegram.org/auth?bot_id=${TELEGRAM_BOT_USERNAME}&origin=${window.location.origin}&request_access=write&return_to=${window.location.origin}/auth/telegram/callback`;
    
    // Open in popup or same window
    const popup = window.open(authUrl, 'telegram-login', 'width=600,height=600');

    // Listen for callback
    window.addEventListener('message', handleTelegramCallback);

    // Cleanup
    const checkPopup = setInterval(() => {
      if (!popup || popup.closed) {
        clearInterval(checkPopup);
        setIsLoading(false);
        window.removeEventListener('message', handleTelegramCallback);
      }
    }, 1000);
  };

  const handleTelegramCallback = async (event) => {
    // Verify origin
    if (event.origin !== window.location.origin) {
      return;
    }

    const { telegramData } = event.data;
    if (!telegramData) {
      return;
    }

    try {
      // Send to backend
      const response = await fetch(`${API_BASE_URL}/api/auth/telegram/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(telegramData),
      });

      if (!response.ok) {
        throw new Error('Authentication failed');
      }

      const data = await response.json();

      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      if (onAuth) {
        onAuth(data);
      }
    } catch (error) {
      console.error('Telegram auth error:', error);
      alert('Failed to sign in with Telegram.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleLogin}
      disabled={isLoading}
      className="telegram-login-button"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '12px 24px',
        backgroundColor: '#0088cc',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        fontSize: '16px',
        cursor: 'pointer',
        fontWeight: '600',
      }}
    >
      <TelegramIcon />
      {isLoading ? 'Connecting...' : 'Sign in with Telegram'}
    </button>
  );
};

// ============================================================================
// Login Page Example
// ============================================================================

export const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();

      // Store tokens
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      alert('Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTelegramAuth = (data) => {
    console.log('Telegram auth successful:', data);
    // Redirect to dashboard
    navigate('/dashboard');
  };

  return (
    <div className="login-container" style={{ maxWidth: '400px', margin: '100px auto', padding: '20px' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>Sign In</h1>

      {/* Email/Password Form */}
      <form onSubmit={handleEmailLogin}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: '5px' }}>
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd',
            }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: '5px' }}>
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd',
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '16px',
            cursor: 'pointer',
            fontWeight: '600',
          }}
        >
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>

      {/* Divider */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        margin: '30px 0',
        gap: '10px'
      }}>
        <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
        <span style={{ color: '#666', fontSize: '14px' }}>OR</span>
        <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
      </div>

      {/* Telegram Login Widget */}
      <div style={{ textAlign: 'center' }}>
        <TelegramLoginWidget onAuth={handleTelegramAuth} />
        {/* OR use manual button: */}
        {/* <TelegramLoginButton onAuth={handleTelegramAuth} /> */}
      </div>

      {/* Additional Links */}
      <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '14px', color: '#666' }}>
        <a href="/forgot-password" style={{ color: '#0088cc', textDecoration: 'none' }}>
          Forgot password?
        </a>
        {' • '}
        <a href="/register" style={{ color: '#0088cc', textDecoration: 'none' }}>
          Create account
        </a>
      </div>
    </div>
  );
};

// ============================================================================
// Profile Settings - Link Telegram Account
// ============================================================================

export const ProfileTelegramLink = () => {
  const [user, setUser] = useState(null);
  const [isLinked, setIsLinked] = useState(false);

  useEffect(() => {
    // Load user from localStorage
    const userData = JSON.parse(localStorage.getItem('user') || '{}');
    setUser(userData);
    setIsLinked(!!userData.telegram_id);
  }, []);

  const handleLinkTelegram = async (telegramData) => {
    try {
      const accessToken = localStorage.getItem('access_token');

      const response = await fetch(`${API_BASE_URL}/api/auth/telegram/link`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ telegram_data: telegramData }),
      });

      if (!response.ok) {
        throw new Error('Failed to link Telegram account');
      }

      const data = await response.json();
      
      // Update user data
      const updatedUser = { ...user, telegram_id: data.telegram_id };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);
      setIsLinked(true);

      alert('Telegram account linked successfully!');
    } catch (error) {
      console.error('Error linking Telegram:', error);
      alert('Failed to link Telegram account.');
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h3>Telegram Integration</h3>
      
      {isLinked ? (
        <div>
          <p style={{ color: 'green' }}>✓ Telegram account linked</p>
          <p>Username: @{user.telegram_username || 'N/A'}</p>
          <p>You can now sign in using Telegram without a password!</p>
        </div>
      ) : (
        <div>
          <p>Link your Telegram account for faster login</p>
          <TelegramLoginWidget onAuth={handleLinkTelegram} />
        </div>
      )}
    </div>
  );
};

// ============================================================================
// Telegram Icon Component
// ============================================================================

const TelegramIcon = () => (
  <svg 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="currentColor"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161l-1.884 8.876c-.141.631-.513.784-1.038.489l-2.871-2.116-1.384 1.332c-.153.153-.281.281-.576.281l.206-2.901 5.305-4.792c.231-.206-.05-.32-.357-.114l-6.558 4.126-2.829-.888c-.615-.192-.628-.615.128-.91l11.055-4.26c.512-.192.96.114.794.91z"/>
  </svg>
);

// ============================================================================
// Usage in Your App
// ============================================================================

/*

// In your App.js or routes:

import { LoginPage, ProfileTelegramLink } from './components/TelegramLogin';

// Add to routes:
<Route path="/login" element={<LoginPage />} />
<Route path="/profile" element={<ProfileTelegramLink />} />

// Environment Variables (.env):
REACT_APP_TELEGRAM_BOT_USERNAME=YourAnalyticBot
REACT_APP_API_URL=http://localhost:8000

*/
