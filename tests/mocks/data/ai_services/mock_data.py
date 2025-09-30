"""
AI Services Mock Data Module
Extracted from ai_services.py to maintain clean separation of mock data
Provides rich demo experiences for AI-powered features
"""


def get_mock_churn_prediction(demo_type: str = "full_featured") -> dict:
    """Generate mock churn prediction data"""
    base_predictions = {
        "full_featured": {
            "churn_probability": 0.15,
            "risk_level": "low",
            "confidence_score": 0.87,
            "key_factors": [
                "Consistent engagement patterns",
                "Active content creation",
                "High interaction rates"
            ],
            "immediate_actions": [
                "Continue current content strategy",
                "Engage with trending topics",
                "Monitor performance metrics"
            ]
        },
        "read_only": {
            "churn_probability": 0.32,
            "risk_level": "medium",
            "confidence_score": 0.76,
            "key_factors": [
                "Declining engagement",
                "Reduced posting frequency"
            ],
            "immediate_actions": [
                "Increase content variety",
                "Analyze top performing posts"
            ]
        },
        "limited": {
            "churn_probability": 0.08,
            "risk_level": "low",
            "confidence_score": 0.92,
            "key_factors": [
                "New user with growth potential"
            ],
            "immediate_actions": [
                "Explore platform features"
            ]
        }
    }
    
    return base_predictions.get(demo_type, base_predictions["limited"])


def get_mock_security_analysis(demo_type: str = "full_featured", content: str = None) -> dict:
    """Generate mock security analysis data"""
    base_analysis = {
        "full_featured": {
            "threat_level": "low",
            "security_score": 94.2,
            "detected_risks": [
                "Minor: Potential phishing link detected (false positive)",
                "Info: High engagement content"
            ],
            "recommendations": [
                "Enable 2FA for enhanced security",
                "Monitor unusual activity patterns",
                "Review content engagement metrics",
                "Consider premium security features"
            ],
            "analysis_metadata": {
                "scan_duration": "0.3s",
                "rules_applied": 47,
                "confidence": 0.94
            }
        },
        "read_only": {
            "threat_level": "low",
            "security_score": 88.5,
            "detected_risks": [],
            "recommendations": [
                "Enable 2FA",
                "Review account permissions"
            ],
            "analysis_metadata": {
                "scan_duration": "0.2s",
                "rules_applied": 23,
                "confidence": 0.88
            }
        },
        "limited": {
            "threat_level": "low",
            "security_score": 92.0,
            "detected_risks": [],
            "recommendations": [
                "Complete security setup",
                "Enable account monitoring"
            ],
            "analysis_metadata": {
                "scan_duration": "0.1s",
                "rules_applied": 12,
                "confidence": 0.92
            }
        },
        "admin": {
            "threat_level": "medium",
            "security_score": 76.8,
            "detected_risks": [
                "High: Admin privileges in use",
                "Medium: Multiple active sessions",
                "Info: Advanced feature access"
            ],
            "recommendations": [
                "Enable MFA for admin accounts",
                "Review active sessions regularly",
                "Monitor privileged operations",
                "Implement session timeout policies"
            ],
            "analysis_metadata": {
                "scan_duration": "0.5s",
                "rules_applied": 73,
                "confidence": 0.87
            }
        }
    }
    
    analysis = base_analysis.get(demo_type, base_analysis["limited"]).copy()
    
    # Modify based on content if provided
    if content and any(keyword in content.lower() for keyword in ["hack", "malicious", "spam", "phishing"]):
        analysis["threat_level"] = "high" if demo_type == "admin" else "medium"
        analysis["security_score"] = max(45.0, analysis["security_score"] - 25.0)
        analysis["detected_risks"].append("Suspicious content patterns detected")
        analysis["recommendations"].append("Review content for policy violations")
    
    return analysis


def get_mock_content_optimization(demo_type: str = "full_featured") -> dict:
    """Generate mock content optimization suggestions"""
    base_optimization = {
        "full_featured": {
            "optimization_score": 87.3,
            "suggestions": [
                "Add trending hashtags: #TechNews #Innovation",
                "Optimal posting time: 2:00 PM - 4:00 PM",
                "Consider adding video content for 40% higher engagement",
                "Use emojis to increase readability by 15%"
            ],
            "predicted_engagement": {
                "views": 12500,
                "likes": 845,
                "shares": 127,
                "comments": 89
            },
            "improvement_potential": "+23% engagement"
        },
        "read_only": {
            "optimization_score": 73.1,
            "suggestions": [
                "Add relevant hashtags",
                "Post during peak hours"
            ],
            "predicted_engagement": {
                "views": 3200,
                "likes": 156,
                "shares": 23,
                "comments": 12
            },
            "improvement_potential": "+15% engagement"
        },
        "limited": {
            "optimization_score": 68.5,
            "suggestions": [
                "Include call-to-action",
                "Add visual content"
            ],
            "predicted_engagement": {
                "views": 850,
                "likes": 67,
                "shares": 8,
                "comments": 3
            },
            "improvement_potential": "+12% engagement"
        }
    }
    
    return base_optimization.get(demo_type, base_optimization["limited"])


def get_mock_trending_analysis(demo_type: str = "full_featured") -> dict:
    """Generate mock trending topics analysis"""
    base_trends = {
        "full_featured": {
            "trending_topics": [
                {
                    "topic": "AI and Machine Learning",
                    "trend_score": 94.2,
                    "volume": 45780,
                    "sentiment": "positive",
                    "related_hashtags": ["#AI", "#MachineLearning", "#TechTrends"]
                },
                {
                    "topic": "Sustainable Technology",
                    "trend_score": 87.6,
                    "volume": 23450,
                    "sentiment": "positive",
                    "related_hashtags": ["#GreenTech", "#Sustainability", "#CleanEnergy"]
                },
                {
                    "topic": "Cryptocurrency Updates",
                    "trend_score": 76.3,
                    "volume": 67890,
                    "sentiment": "mixed",
                    "related_hashtags": ["#Crypto", "#Bitcoin", "#Blockchain"]
                }
            ],
            "recommendations": [
                "Create content around AI trends for maximum visibility",
                "Consider sustainability angle for broader appeal",
                "Monitor crypto sentiment before posting related content"
            ]
        },
        "read_only": {
            "trending_topics": [
                {
                    "topic": "Technology News", 
                    "trend_score": 82.1,
                    "volume": 12500,
                    "sentiment": "positive",
                    "related_hashtags": ["#Tech", "#News"]
                }
            ],
            "recommendations": [
                "Follow tech news trends",
                "Engage with trending topics"
            ]
        },
        "limited": {
            "trending_topics": [
                {
                    "topic": "General Interest",
                    "trend_score": 65.3, 
                    "volume": 5600,
                    "sentiment": "neutral",
                    "related_hashtags": ["#Updates"]
                }
            ],
            "recommendations": [
                "Explore trending topics",
                "Build audience engagement"
            ]
        }
    }
    
    return base_trends.get(demo_type, base_trends["limited"])