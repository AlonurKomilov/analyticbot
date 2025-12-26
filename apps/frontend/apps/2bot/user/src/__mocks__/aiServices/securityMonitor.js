/**
 * Security Monitor Service Mock Data
 * Mock data for security monitoring AI service including threat detection and security analysis
 */

export const securityStats = {
    threatsDetected: 156,
    threatsBlocked: 143,
    securityScore: 94,
    status: 'active'
};

export const mockSecurityAlerts = [
    {
        id: 'SEC-2024-001',
        severity: 'Critical',
        type: 'Suspicious Login',
        timestamp: '2024-01-15T10:30:22Z',
        description: 'Multiple failed login attempts from unusual location',
        source: 'Authentication System',
        ipAddress: '192.168.1.100',
        location: 'Unknown Location, RU',
        userId: 'user_12345',
        status: 'Investigating',
        riskScore: 95,
        evidence: [
            '15 failed login attempts in 5 minutes',
            'IP address not seen before',
            'Geolocation inconsistent with user profile',
            'User agent suggests automated tool'
        ],
        actions: [
            'Account temporarily locked',
            'Security team notified',
            'IP address blocked',
            'User contacted via verified email'
        ]
    },
    {
        id: 'SEC-2024-002',
        severity: 'High',
        type: 'Data Exfiltration',
        timestamp: '2024-01-15T09:15:43Z',
        description: 'Unusual data access pattern detected',
        source: 'Data Access Monitor',
        ipAddress: '10.0.1.50',
        location: 'Internal Network',
        userId: 'admin_789',
        status: 'Resolved',
        riskScore: 78,
        evidence: [
            'Accessed 50+ user records in rapid succession',
            'Downloads during off-hours',
            'Pattern inconsistent with normal admin behavior',
            'Large file transfers detected'
        ],
        actions: [
            'Access logs reviewed',
            'Admin account privileges verified',
            'Legitimate business activity confirmed',
            'Additional monitoring implemented'
        ]
    },
    {
        id: 'SEC-2024-003',
        severity: 'Medium',
        type: 'Malware Detection',
        timestamp: '2024-01-15T08:45:12Z',
        description: 'Potentially malicious file upload detected',
        source: 'File Scanner',
        ipAddress: '203.0.113.45',
        location: 'San Francisco, US',
        userId: 'creator_456',
        status: 'Blocked',
        riskScore: 65,
        evidence: [
            'File contains obfuscated JavaScript',
            'Matches signature of known malware family',
            'Suspicious network behavior patterns',
            'File entropy suggests encryption/packing'
        ],
        actions: [
            'File upload blocked',
            'File quarantined for analysis',
            'User notified of security issue',
            'Antivirus definitions updated'
        ]
    }
];

export const threatCategories = [
    {
        category: 'Authentication Threats',
        count: 45,
        trend: '+12%',
        color: '#f44336',
        subcategories: [
            'Brute Force Attacks',
            'Credential Stuffing',
            'Session Hijacking',
            'Multi-Factor Bypass'
        ]
    },
    {
        category: 'Data Security',
        count: 28,
        trend: '-8%',
        color: '#ff9800',
        subcategories: [
            'Unauthorized Access',
            'Data Exfiltration',
            'Privacy Violations',
            'Data Corruption'
        ]
    },
    {
        category: 'Network Security',
        count: 67,
        trend: '+23%',
        color: '#2196f3',
        subcategories: [
            'DDoS Attempts',
            'Port Scanning',
            'Intrusion Attempts',
            'Malicious Traffic'
        ]
    },
    {
        category: 'Malware & Files',
        count: 16,
        trend: '-15%',
        color: '#9c27b0',
        subcategories: [
            'Virus Detection',
            'Trojan Analysis',
            'Suspicious Scripts',
            'File Corruption'
        ]
    }
];

export const securityMetrics = [
    {
        metric: 'Response Time',
        value: '2.3s',
        target: '< 5s',
        status: 'good',
        description: 'Average time to detect and respond to threats'
    },
    {
        metric: 'False Positive Rate',
        value: '3.2%',
        target: '< 5%',
        status: 'good',
        description: 'Percentage of legitimate activities flagged as threats'
    },
    {
        metric: 'Coverage Score',
        value: '96.8%',
        target: '> 95%',
        status: 'excellent',
        description: 'Percentage of system components under monitoring'
    },
    {
        metric: 'Threat Block Rate',
        value: '91.7%',
        target: '> 90%',
        status: 'good',
        description: 'Percentage of threats successfully blocked'
    }
];

export const riskAssessment = {
    overallRisk: 'Medium',
    riskScore: 65,
    factors: [
        {
            factor: 'External Threat Landscape',
            risk: 'High',
            score: 78,
            description: 'Increased targeting by sophisticated threat actors'
        },
        {
            factor: 'System Vulnerabilities',
            risk: 'Low',
            score: 25,
            description: 'Recent security patches and updates applied'
        },
        {
            factor: 'User Behavior',
            risk: 'Medium',
            score: 55,
            description: 'Some users showing risky security practices'
        },
        {
            factor: 'Infrastructure Security',
            risk: 'Low',
            score: 30,
            description: 'Strong network security controls in place'
        }
    ],
    recommendations: [
        'Implement additional user security training',
        'Consider upgrading firewall rules',
        'Review access control policies',
        'Enhance monitoring for external threats'
    ]
};

export const securityTrends = [
    { date: '2024-01-01', threats: 12, blocked: 11 },
    { date: '2024-01-02', threats: 18, blocked: 16 },
    { date: '2024-01-03', threats: 8, blocked: 8 },
    { date: '2024-01-04', threats: 25, blocked: 23 },
    { date: '2024-01-05', threats: 15, blocked: 14 },
    { date: '2024-01-06', threats: 32, blocked: 29 },
    { date: '2024-01-07', threats: 19, blocked: 18 },
    { date: '2024-01-08', threats: 22, blocked: 21 },
    { date: '2024-01-09', threats: 16, blocked: 15 },
    { date: '2024-01-10', threats: 28, blocked: 26 },
    { date: '2024-01-11', threats: 21, blocked: 20 },
    { date: '2024-01-12', threats: 17, blocked: 16 },
    { date: '2024-01-13', threats: 24, blocked: 23 },
    { date: '2024-01-14', threats: 13, blocked: 13 },
    { date: '2024-01-15', threats: 30, blocked: 27 }
];

export const complianceStatus = {
    frameworks: [
        {
            name: 'SOC 2 Type II',
            status: 'Compliant',
            lastAudit: '2023-12-15',
            nextAudit: '2024-12-15',
            score: 98
        },
        {
            name: 'ISO 27001',
            status: 'Compliant',
            lastAudit: '2023-11-20',
            nextAudit: '2024-11-20',
            score: 96
        },
        {
            name: 'GDPR',
            status: 'Compliant',
            lastAudit: '2023-10-30',
            nextAudit: '2024-04-30',
            score: 94
        },
        {
            name: 'HIPAA',
            status: 'Not Applicable',
            lastAudit: null,
            nextAudit: null,
            score: null
        }
    ]
};

export const securitySettings = {
    alertThresholds: {
        critical: 90,
        high: 70,
        medium: 50,
        low: 30
    },
    autoResponse: {
        enabled: true,
        blockSuspiciousIPs: true,
        quarantineFiles: true,
        lockCompromisedAccounts: true
    },
    monitoringScope: {
        authentication: true,
        fileUploads: true,
        dataAccess: true,
        networkTraffic: true,
        apiCalls: true
    },
    reportingFrequency: 'daily',
    retentionPeriod: '90 days'
};

export default {
    securityStats,
    mockSecurityAlerts,
    threatCategories,
    securityMetrics,
    riskAssessment,
    securityTrends,
    complianceStatus,
    securitySettings
};
