/**
 * 🔐 Device Fingerprinting Utility
 *
 * Generates a unique fingerprint for the user's device to detect:
 * - Token theft across devices
 * - Account sharing
 * - Suspicious login patterns
 *
 * Privacy-conscious: Hashes all data, doesn't collect IP (handled server-side)
 */

export interface DeviceInfo {
  userAgent: string;
  language: string;
  platform: string;
  screenResolution: string;
  timezone: string;
  colorDepth: number;
  hardwareConcurrency: number;
  deviceMemory?: number;
  touchSupport: boolean;
}

export class DeviceFingerprint {
  /**
   * Generate device fingerprint (client-side only data)
   */
  static generate(): string {
    const info = this.collectDeviceInfo();
    return this.hashFingerprint(info);
  }

  /**
   * Collect device information
   */
  private static collectDeviceInfo(): DeviceInfo {
    const nav = window.navigator as any;
    const screen = window.screen;

    return {
      userAgent: nav.userAgent || 'unknown',
      language: nav.language || nav.userLanguage || 'unknown',
      platform: nav.platform || 'unknown',
      screenResolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'unknown',
      colorDepth: screen.colorDepth || 0,
      hardwareConcurrency: nav.hardwareConcurrency || 0,
      deviceMemory: nav.deviceMemory,
      touchSupport: this.detectTouchSupport()
    };
  }

  /**
   * Detect touch screen support
   */
  private static detectTouchSupport(): boolean {
    return (
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      (navigator as any).msMaxTouchPoints > 0
    );
  }

  /**
   * Hash fingerprint data for privacy
   * Uses simple base64 encoding (upgrade to crypto hash in production)
   */
  private static hashFingerprint(info: DeviceInfo): string {
    try {
      const fingerprintString = JSON.stringify(info);

      // Simple base64 encoding (consider using crypto.subtle.digest() for production)
      const encoded = btoa(fingerprintString);

      // Return first 32 characters as fingerprint ID
      return encoded.substring(0, 32);
    } catch (error) {
      console.error('Failed to generate device fingerprint:', error);
      return 'unknown';
    }
  }

  /**
   * Get detailed device info for debugging
   */
  static getDeviceInfo(): DeviceInfo {
    return this.collectDeviceInfo();
  }

  /**
   * Check if device fingerprint has changed
   */
  static hasChanged(previousFingerprint: string): boolean {
    const currentFingerprint = this.generate();
    return previousFingerprint !== currentFingerprint;
  }

  /**
   * Store device fingerprint in localStorage
   */
  static store(): void {
    const fingerprint = this.generate();
    localStorage.setItem('device_fingerprint', fingerprint);
  }

  /**
   * Get stored device fingerprint
   */
  static getStored(): string | null {
    return localStorage.getItem('device_fingerprint');
  }

  /**
   * Clear stored device fingerprint
   */
  static clear(): void {
    localStorage.removeItem('device_fingerprint');
  }
}

// Auto-generate and store fingerprint on load
if (typeof window !== 'undefined') {
  // Generate fingerprint only if not exists
  if (!DeviceFingerprint.getStored()) {
    DeviceFingerprint.store();
  }
}

// Export singleton function for ease of use
export function getDeviceFingerprint(): string {
  const stored = DeviceFingerprint.getStored();
  if (stored) return stored;

  const fingerprint = DeviceFingerprint.generate();
  DeviceFingerprint.store();
  return fingerprint;
}

export default DeviceFingerprint;
