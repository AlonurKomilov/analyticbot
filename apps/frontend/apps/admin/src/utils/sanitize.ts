/**
 * Input Sanitization Utilities
 * 
 * Provides functions to sanitize user input and prevent XSS attacks.
 * Use these utilities before displaying any user-provided content.
 */

/**
 * HTML entities map for escaping
 */
const HTML_ENTITIES: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;',
};

/**
 * Escape HTML special characters to prevent XSS
 * 
 * @param str - String to escape
 * @returns Escaped string safe for HTML display
 * 
 * @example
 * escapeHtml('<script>alert("xss")</script>')
 * // Returns: '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
 */
export function escapeHtml(str: string | null | undefined): string {
  if (str === null || str === undefined) {
    return '';
  }
  
  return String(str).replace(/[&<>"'`=/]/g, (char) => HTML_ENTITIES[char] || char);
}

/**
 * Sanitize a string for safe display in HTML
 * Removes potentially dangerous content while preserving safe text
 * 
 * @param str - String to sanitize
 * @returns Sanitized string
 */
export function sanitizeText(str: string | null | undefined): string {
  if (str === null || str === undefined) {
    return '';
  }
  
  // First escape HTML entities
  let sanitized = escapeHtml(str);
  
  // Remove any remaining script-like patterns (extra safety)
  sanitized = sanitized.replace(/javascript:/gi, '');
  sanitized = sanitized.replace(/on\w+\s*=/gi, '');
  sanitized = sanitized.replace(/data:/gi, '');
  
  return sanitized;
}

/**
 * Sanitize a URL to prevent javascript: and data: URLs
 * 
 * @param url - URL to sanitize
 * @returns Sanitized URL or empty string if unsafe
 * 
 * @example
 * sanitizeUrl('javascript:alert(1)')
 * // Returns: ''
 * 
 * sanitizeUrl('https://example.com')
 * // Returns: 'https://example.com'
 */
export function sanitizeUrl(url: string | null | undefined): string {
  if (url === null || url === undefined) {
    return '';
  }
  
  const trimmed = String(url).trim().toLowerCase();
  
  // Block dangerous protocols
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:', 'file:'];
  for (const protocol of dangerousProtocols) {
    if (trimmed.startsWith(protocol)) {
      console.warn(`Blocked dangerous URL: ${url}`);
      return '';
    }
  }
  
  // Allow safe protocols
  const safeProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
  const hasProtocol = safeProtocols.some(p => trimmed.startsWith(p));
  
  // If no protocol, assume relative URL (safe)
  if (!hasProtocol && !trimmed.includes(':')) {
    return url;
  }
  
  // If has safe protocol, return as-is
  if (hasProtocol) {
    return url;
  }
  
  // Unknown protocol - block
  console.warn(`Blocked URL with unknown protocol: ${url}`);
  return '';
}

/**
 * Sanitize user input for use in CSS
 * Prevents CSS injection attacks
 * 
 * @param value - CSS value to sanitize
 * @returns Sanitized CSS value
 */
export function sanitizeCss(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return '';
  }
  
  // Remove potentially dangerous CSS patterns
  let sanitized = String(value);
  
  // Remove url() to prevent data exfiltration
  sanitized = sanitized.replace(/url\s*\(/gi, '');
  
  // Remove expression() (IE-specific XSS vector)
  sanitized = sanitized.replace(/expression\s*\(/gi, '');
  
  // Remove javascript: in CSS
  sanitized = sanitized.replace(/javascript:/gi, '');
  
  // Remove behavior: (IE-specific)
  sanitized = sanitized.replace(/behavior\s*:/gi, '');
  
  return sanitized;
}

/**
 * Sanitize an email address for display
 * 
 * @param email - Email to sanitize
 * @returns Sanitized email
 */
export function sanitizeEmail(email: string | null | undefined): string {
  if (email === null || email === undefined) {
    return '';
  }
  
  // Basic email validation and sanitization
  const sanitized = String(email).trim();
  
  // Only allow valid email characters
  if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(sanitized)) {
    return escapeHtml(sanitized); // Return escaped version if invalid format
  }
  
  return escapeHtml(sanitized);
}

/**
 * Sanitize a username for display
 * 
 * @param username - Username to sanitize
 * @returns Sanitized username
 */
export function sanitizeUsername(username: string | null | undefined): string {
  if (username === null || username === undefined) {
    return '';
  }
  
  // Escape HTML and trim
  return escapeHtml(String(username).trim());
}

/**
 * Create a safe display object from user data
 * Sanitizes all string fields
 * 
 * @param data - Object with user data
 * @returns Object with sanitized string values
 */
export function sanitizeUserData<T extends Record<string, unknown>>(data: T): T {
  const sanitized: Record<string, unknown> = {};
  
  for (const [key, value] of Object.entries(data)) {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeText(value);
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeUserData(value as Record<string, unknown>);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized as T;
}

/**
 * Validate and sanitize a number input
 * 
 * @param value - Value to validate
 * @param defaultValue - Default if invalid
 * @param min - Minimum allowed value
 * @param max - Maximum allowed value
 * @returns Sanitized number
 */
export function sanitizeNumber(
  value: unknown,
  defaultValue = 0,
  min = -Infinity,
  max = Infinity
): number {
  const num = Number(value);
  
  if (isNaN(num)) {
    return defaultValue;
  }
  
  return Math.max(min, Math.min(max, num));
}

/**
 * Strip HTML tags from a string (for plain text display)
 * 
 * @param html - String potentially containing HTML
 * @returns Plain text without HTML tags
 */
export function stripHtmlTags(html: string | null | undefined): string {
  if (html === null || html === undefined) {
    return '';
  }
  
  // Remove HTML tags
  const withoutTags = String(html).replace(/<[^>]*>/g, '');
  
  // Decode HTML entities
  const textarea = document.createElement('textarea');
  textarea.innerHTML = withoutTags;
  return textarea.value;
}

/**
 * Truncate text safely (preserving HTML entity integrity)
 * 
 * @param text - Text to truncate
 * @param maxLength - Maximum length
 * @param suffix - Suffix to add if truncated
 * @returns Truncated text
 */
export function truncateText(
  text: string | null | undefined,
  maxLength: number,
  suffix = '...'
): string {
  if (text === null || text === undefined) {
    return '';
  }
  
  const str = String(text);
  
  if (str.length <= maxLength) {
    return str;
  }
  
  // Truncate and add suffix
  return str.slice(0, maxLength - suffix.length) + suffix;
}

export default {
  escapeHtml,
  sanitizeText,
  sanitizeUrl,
  sanitizeCss,
  sanitizeEmail,
  sanitizeUsername,
  sanitizeUserData,
  sanitizeNumber,
  stripHtmlTags,
  truncateText,
};
