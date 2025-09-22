"""
AI Services Mock Data Module
Extracted from ai_services.py to maintain clean separation of mock data
"""


def create_mock_security_analysis(content: str = "") -> dict:
    """Create mock security analysis response"""
    threat_level = "low"
    security_score = 92.5
    detected_risks = []
    recommendations = ["Enable 2FA", "Monitor unusual activity"]
    
    # Simple content-based risk detection for demo
    if content and any(keyword in content.lower() 
                      for keyword in ["hack", "malicious", "spam"]):
        threat_level = "medium"
        security_score = 65.0
        detected_risks.append("Suspicious content detected")
        recommendations.append("Review content for policy violations")
    
    return {
        "threat_level": threat_level,
        "security_score": security_score,
        "detected_risks": detected_risks,
        "recommendations": recommendations
    }


def create_mock_content_optimization(content: str = "") -> dict:
    """Create mock content optimization response"""
    return {
        "optimization_score": 78.5,
        "readability_score": 85.2,
        "engagement_prediction": 7.3,
        "suggested_improvements": [
            "Add more engaging call-to-action",
            "Consider shorter paragraphs",
            "Include relevant hashtags"
        ],
        "sentiment_analysis": {
            "overall": "positive",
            "confidence": 0.87
        }
    }


def create_mock_churn_prediction(user_id: str = "") -> dict:
    """Create mock churn prediction response"""
    return {
        "churn_probability": 0.23,
        "risk_level": "low",
        "confidence": 0.91,
        "contributing_factors": [
            "Consistent engagement",
            "Regular posting schedule",
            "Positive user feedback"
        ],
        "retention_recommendations": [
            "Continue current engagement strategy",
            "Consider premium feature promotion"
        ]
    }


def create_mock_ai_service_stats() -> dict:
    """Create mock AI service statistics"""
    return {
        "content_optimizer": {
            "total_analyzed": 1247,
            "avg_improvement": 34.2,
            "status": "active"
        },
        "security_monitor": {
            "threats_detected": 12,
            "security_score": 92.5,
            "status": "active"
        },
        "churn_predictor": {
            "users_analyzed": 892,
            "accuracy": 89.3,
            "status": "beta"
        }
    }