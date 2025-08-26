"""
Multi-Agent System Configuration
Defines workflows, agent configurations, and orchestration rules
"""

from typing import Dict, List, Any
from enum import Enum

class AgentType(str, Enum):
    """Available agent types in the system"""
    MARKET_VALIDATION = "market_validation"
    PRODUCT_ARCHITECT = "product_architect"
    AI_ENGINEERING = "ai_engineering"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    LEGAL_PROTECTION = "legal_protection"
    OPERATIONS = "operations"
    USER_EXPERIENCE = "user_experience"

class WorkflowType(str, Enum):
    """Predefined workflow types"""
    HYPOTHESIS_TO_FEATURE = "hypothesis_to_feature"
    FEATURE_TO_DEPLOYMENT = "feature_to_deployment"
    USER_FEEDBACK_LOOP = "user_feedback_loop"
    MARKET_RESEARCH_SPRINT = "market_research_sprint"
    FULL_STRATEGIC_LOOP = "full_strategic_loop"

# Agent Configurations
AGENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    AgentType.MARKET_VALIDATION: {
        "id": "market_validation_001",
        "name": "Market & Customer Validation Agent",
        "description": "Validates hypotheses through empirical data",
        "queue": "agent_market_validation",
        "timeout": 300,  # 5 minutes
        "retry_policy": {
            "max_retries": 3,
            "retry_delay": 30
        },
        "capabilities": [
            "validate_hypothesis",
            "competitive_analysis",
            "user_survey_creation",
            "interview_design",
            "ab_test_planning"
        ]
    },
    AgentType.PRODUCT_ARCHITECT: {
        "id": "product_architect_001",
        "name": "Product Architect Agent",
        "description": "Strategic visionary for product roadmap",
        "queue": "agent_product_architect",
        "timeout": 180,  # 3 minutes
        "retry_policy": {
            "max_retries": 3,
            "retry_delay": 20
        },
        "capabilities": [
            "backlog_prioritization",
            "feature_evaluation",
            "roadmap_generation",
            "pillar_alignment_check"
        ]
    },
    AgentType.AI_ENGINEERING: {
        "id": "ai_engineering_001",
        "name": "AI & Systems Engineering Agent",
        "description": "Master builder for technical implementation",
        "queue": "agent_ai_engineering",
        "timeout": 600,  # 10 minutes
        "retry_policy": {
            "max_retries": 5,
            "retry_delay": 60
        },
        "capabilities": [
            "technical_planning",
            "code_generation",
            "architecture_design",
            "deployment_orchestration"
        ]
    },
    AgentType.BUSINESS_INTELLIGENCE: {
        "id": "business_intelligence_001",
        "name": "Business Intelligence Agent",
        "description": "Combined growth, marketing, and revenue optimization",
        "queue": "agent_business_intelligence",
        "timeout": 300,
        "retry_policy": {
            "max_retries": 3,
            "retry_delay": 30
        },
        "capabilities": [
            "marketing_strategy",
            "campaign_execution",
            "metrics_analysis",
            "revenue_optimization"
        ]
    },
    AgentType.USER_EXPERIENCE: {
        "id": "user_experience_001",
        "name": "User Experience Agent",
        "description": "User advocate and community manager",
        "queue": "agent_user_experience",
        "timeout": 180,
        "retry_policy": {
            "max_retries": 3,
            "retry_delay": 20
        },
        "capabilities": [
            "feedback_analysis",
            "support_automation",
            "community_engagement",
            "sentiment_tracking"
        ]
    }
}

# Workflow Definitions
WORKFLOW_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    WorkflowType.HYPOTHESIS_TO_FEATURE: {
        "name": "Hypothesis to Feature",
        "description": "Validate hypothesis and create prioritized feature",
        "agent_sequence": [
            AgentType.MARKET_VALIDATION,
            AgentType.PRODUCT_ARCHITECT
        ],
        "timeout": 900,  # 15 minutes total
        "parallel_steps": []
    },
    WorkflowType.FEATURE_TO_DEPLOYMENT: {
        "name": "Feature to Deployment",
        "description": "Build and deploy a prioritized feature",
        "agent_sequence": [
            AgentType.PRODUCT_ARCHITECT,
            AgentType.AI_ENGINEERING,
            AgentType.BUSINESS_INTELLIGENCE
        ],
        "timeout": 1800,  # 30 minutes total
        "parallel_steps": []
    },
    WorkflowType.USER_FEEDBACK_LOOP: {
        "name": "User Feedback Loop",
        "description": "Process user feedback into actionable insights",
        "agent_sequence": [
            AgentType.USER_EXPERIENCE,
            AgentType.PRODUCT_ARCHITECT,
            AgentType.MARKET_VALIDATION
        ],
        "timeout": 1200,  # 20 minutes
        "parallel_steps": []
    },
    WorkflowType.FULL_STRATEGIC_LOOP: {
        "name": "Full Strategic Loop",
        "description": "Complete cycle from hypothesis to deployment with feedback",
        "agent_sequence": [
            AgentType.MARKET_VALIDATION,
            AgentType.PRODUCT_ARCHITECT,
            AgentType.AI_ENGINEERING,
            AgentType.BUSINESS_INTELLIGENCE,
            AgentType.USER_EXPERIENCE
        ],
        "timeout": 3600,  # 1 hour
        "parallel_steps": [
            # Business Intelligence and User Experience can run in parallel after deployment
            [AgentType.BUSINESS_INTELLIGENCE, AgentType.USER_EXPERIENCE]
        ]
    }
}

# Agent Communication Rules
COMMUNICATION_RULES = {
    "message_ttl": 3600,  # 1 hour
    "max_message_size": 1048576,  # 1MB
    "priority_levels": {
        "critical": 10,
        "high": 8,
        "normal": 5,
        "low": 3
    },
    "event_retention": 86400 * 7,  # 7 days
    "workflow_retention": 86400 * 30  # 30 days
}

# Performance SLAs
PERFORMANCE_SLAS = {
    "agent_startup_time": 5.0,  # seconds
    "message_processing_time": {
        AgentType.MARKET_VALIDATION: 60.0,
        AgentType.PRODUCT_ARCHITECT: 30.0,
        AgentType.AI_ENGINEERING: 120.0,
        AgentType.BUSINESS_INTELLIGENCE: 45.0,
        AgentType.USER_EXPERIENCE: 20.0
    },
    "workflow_completion_time": {
        WorkflowType.HYPOTHESIS_TO_FEATURE: 600.0,
        WorkflowType.FEATURE_TO_DEPLOYMENT: 1200.0,
        WorkflowType.USER_FEEDBACK_LOOP: 900.0,
        WorkflowType.FULL_STRATEGIC_LOOP: 2400.0
    }
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "metrics_interval": 60,  # seconds
    "health_check_interval": 30,  # seconds
    "alert_thresholds": {
        "error_rate": 0.05,  # 5%
        "latency_p95": 2000,  # 2 seconds
        "queue_depth": 100,
        "memory_usage": 0.8  # 80%
    },
    "dashboard_refresh": 5  # seconds
}

# External Service Integrations
EXTERNAL_SERVICES = {
    "market_research": {
        "crunchbase": {
            "enabled": False,
            "api_key_env": "CRUNCHBASE_API_KEY",
            "rate_limit": 100  # requests per hour
        },
        "google_trends": {
            "enabled": False,
            "rate_limit": 50
        }
    },
    "competitor_monitoring": {
        "similarweb": {
            "enabled": False,
            "api_key_env": "SIMILARWEB_API_KEY",
            "rate_limit": 200
        }
    },
    "customer_feedback": {
        "typeform": {
            "enabled": False,
            "api_key_env": "TYPEFORM_API_KEY"
        },
        "hotjar": {
            "enabled": False,
            "api_key_env": "HOTJAR_API_KEY"
        }
    }
}

# Feature Flags for Gradual Rollout
FEATURE_FLAGS = {
    "enable_multi_agent_system": False,
    "enable_parallel_workflows": False,
    "enable_external_integrations": False,
    "enable_ml_optimization": False,
    "enable_auto_scaling": False,
    "debug_mode": True
}

def get_agent_config(agent_type: AgentType) -> Dict[str, Any]:
    """Get configuration for a specific agent type"""
    return AGENT_CONFIGS.get(agent_type, {})

def get_workflow_definition(workflow_type: WorkflowType) -> Dict[str, Any]:
    """Get definition for a specific workflow"""
    return WORKFLOW_DEFINITIONS.get(workflow_type, {})

def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURE_FLAGS.get(feature, False)