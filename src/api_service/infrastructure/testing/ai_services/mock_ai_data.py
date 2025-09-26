"""
AI Services Mock Data Module
Comprehensive AI services mock data consolidated from frontend and backend.
Extracted from ai_services.py to maintain clean separation of mock data.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..constants import (
    DEFAULT_DEMO_USER_ID,
    DEFAULT_DEMO_USERNAME,
    DEFAULT_DEMO_ENGAGEMENT_RATE
)


def get_content_optimizer_stats() -> Dict[str, Any]:
    """
    Get content optimizer service statistics
    Consolidated from frontend contentOptimizer.js
    """
    return {
        "total_optimized": 1247,
        "today_optimized": 23,
        "avg_improvement": "+34%",
        "status": "active",
        "accuracy_rate": 0.89,
        "processing_time_avg": "1.2s"
    }


def get_recent_optimizations(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent content optimizations
    Consolidated from frontend contentOptimizer.js
    """
    content_types = [
        "Product Launch Post", "Weekly Newsletter", "Tutorial Content",
        "Marketing Campaign", "Social Media Post", "Blog Article",
        "Email Template", "Advertisement Copy"
    ]
    
    optimizations = []
    for i in range(limit):
        original_score = random.randint(45, 75)
        optimized_score = random.randint(80, 98)
        improvement = round(((optimized_score - original_score) / original_score) * 100)
        
        optimizations.append({
            "id": i + 1,
            "content": random.choice(content_types),
            "improvement": f"+{improvement}%",
            "timestamp": f"{random.randint(1, 60)} minutes ago",
            "status": "success",
            "original_score": original_score,
            "optimized_score": optimized_score,
            "suggestions": [
                "Added emotional triggers",
                "Improved call-to-action", 
                "Optimized hashtags",
                "Enhanced readability"
            ][:random.randint(2, 4)]
        })
    
    return optimizations


def get_churn_predictor_stats() -> Dict[str, Any]:
    """
    Get churn predictor service statistics
    Consolidated from frontend churnPredictor.js
    """
    return {
        "users_analyzed": 892,
        "high_risk_users": 47,
        "retention_success": "78%",
        "churn_rate": "12.3%",
        "saved_customers": 23,
        "status": "beta"
    }


def get_churn_predictions(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get user churn risk predictions
    Consolidated from frontend churnPredictor.js
    """
    predictions = []
    risk_levels = ["Low", "Medium", "High", "Critical"]
    subscription_tiers = ["free", "basic", "premium", "enterprise"]
    
    for i in range(limit):
        churn_prob = random.uniform(0.1, 0.95)
        risk_level = (
            "Critical" if churn_prob > 0.8 else
            "High" if churn_prob > 0.6 else
            "Medium" if churn_prob > 0.3 else "Low"
        )
        
        predictions.append({
            "user_id": DEFAULT_DEMO_USER_ID + i,
            "user_name": f"{DEFAULT_DEMO_USERNAME}_{i+1}",
            "churn_probability": round(churn_prob, 2),
            "risk_level": risk_level,
            "last_activity": f"{random.randint(1, 14)} days ago",
            "engagement_score": round(random.uniform(0.1, 0.8), 2),
            "subscription_tier": random.choice(subscription_tiers),
            "key_factors": [
                f"Declining engagement rate (-{random.randint(20, 60)}% last 30 days)",
                f"Reduced posting frequency ({random.randint(1, 3)}x per week)",
                "Fewer interactions with other users",
                "Decreased session duration"
            ][:random.randint(2, 4)]
        })
    
    return predictions


def get_predictive_analytics_stats() -> Dict[str, Any]:
    """
    Get predictive analytics service statistics
    Consolidated from frontend predictiveAnalytics.js
    """
    return {
        "predictions_made": 15678,
        "accuracy_rate": "87.3%",
        "models_active": 12,
        "data_points_processed": "2.4M",
        "last_updated": datetime.now().isoformat(),
        "status": "operational"
    }


def get_security_monitor_stats() -> Dict[str, Any]:
    """
    Get security monitor service statistics
    Consolidated from frontend securityMonitor.js
    """
    return {
        "threats_detected": 156,
        "threats_blocked": 147,
        "security_score": 94.2,
        "last_scan": datetime.now().isoformat(),
        "active_rules": 23,
        "status": "monitoring"
    }


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