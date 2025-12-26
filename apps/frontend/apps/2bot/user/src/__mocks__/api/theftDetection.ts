/**
 * Mock Theft Detection API
 * Provides mock data for content theft detection in demo mode
 */

export type ScanStatus = 'clean' | 'threat' | 'confirmed' | 'suspected';

export interface ScanMatch {
  id: number;
  url: string;
  platform: string;
  matchPercentage: number;
  lastSeen: Date;
  status: ScanStatus;
}

export interface ScanHistoryItem {
  id: number;
  contentHash: string;
  timestamp: Date;
  status: 'clean' | 'threat';
  matchCount: number;
}

export interface ScanStats {
  totalScans: number;
  threatsDetected: number;
  cleanScans: number;
}

/**
 * Generate mock scan results for a content hash
 */
export const generateMockScanResults = (contentHash: string): ScanMatch[] => {
  // If hash is short or starts with 'clean', return no results
  if (contentHash.length < 5 || contentHash.toLowerCase().startsWith('clean')) {
    return [];
  }

  // Otherwise return mock theft detections
  return [
    {
      id: 1,
      url: 'https://example-thief1.com/stolen-content',
      platform: 'Website',
      matchPercentage: 95,
      lastSeen: new Date(Date.now() - 86400000), // 1 day ago
      status: 'confirmed'
    },
    {
      id: 2,
      url: 'https://social-platform.com/user/post/123',
      platform: 'Social Media',
      matchPercentage: 87,
      lastSeen: new Date(Date.now() - 172800000), // 2 days ago
      status: 'suspected'
    },
    {
      id: 3,
      url: 'https://another-site.com/gallery/image',
      platform: 'Image Gallery',
      matchPercentage: 92,
      lastSeen: new Date(Date.now() - 259200000), // 3 days ago
      status: 'confirmed'
    }
  ];
};

/**
 * Generate mock scan history
 */
export const generateMockScanHistory = (): ScanHistoryItem[] => {
  return [
    {
      id: 1,
      contentHash: 'abc123def456...',
      timestamp: new Date(Date.now() - 86400000),
      status: 'clean',
      matchCount: 0
    },
    {
      id: 2,
      contentHash: 'ghi789jkl012...',
      timestamp: new Date(Date.now() - 172800000),
      status: 'threat',
      matchCount: 3
    },
    {
      id: 3,
      contentHash: 'mno345pqr678...',
      timestamp: new Date(Date.now() - 259200000),
      status: 'threat',
      matchCount: 2
    },
    {
      id: 4,
      contentHash: 'stu901vwx234...',
      timestamp: new Date(Date.now() - 345600000),
      status: 'clean',
      matchCount: 0
    }
  ];
};

/**
 * Generate mock scan statistics
 */
export const generateMockStats = (): ScanStats => {
  return {
    totalScans: 25,
    threatsDetected: 3,
    cleanScans: 22
  };
};

/**
 * Simulate API delay for realistic demo experience
 */
export const mockScanDelay = (ms: number = 2000): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Pre-defined mock scenarios for different content hashes
 */
export const mockScanScenarios = {
  clean: {
    hash: 'clean123',
    results: [] as ScanMatch[]
  },
  threat: {
    hash: 'threat456',
    results: generateMockScanResults('threat456')
  },
  highRisk: {
    hash: 'highrisk789',
    results: [
      {
        id: 1,
        url: 'https://major-thief.com/stolen-content',
        platform: 'Website',
        matchPercentage: 99,
        lastSeen: new Date(Date.now() - 3600000),
        status: 'confirmed'
      },
      {
        id: 2,
        url: 'https://content-farm.com/copied-posts',
        platform: 'Content Farm',
        matchPercentage: 98,
        lastSeen: new Date(Date.now() - 7200000),
        status: 'confirmed'
      }
    ]
  }
};
