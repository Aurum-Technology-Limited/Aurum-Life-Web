# Aurum Life API Documentation

**Version:** 1.0.0  
**Base URL:** `https://api.aurumlife.com`  
**Last Updated:** January 2025

---

## 🔐 Authentication

All API requests require authentication using JWT tokens obtained through the login endpoint.

### Headers
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

### Authentication Endpoints

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Error Responses:**
- `401`: Invalid credentials
- `422`: Validation error

---

## 🤖 AI/HRM Endpoints

### GET `/api/insights/{entity_type}/{entity_id}`
Get AI-generated insights for a specific entity.

**Path Parameters:**
- `entity_type`: One of `pillar`, `area`, `project`, `task`
- `entity_id`: UUID of the entity

**Query Parameters:**
- `limit` (optional): Number of insights to return (default: 10)
- `active_only` (optional): Only return active insights (default: true)

**Response 200:**
```json
{
  "insights": [
    {
      "id": "uuid",
      "entity_type": "task",
      "entity_id": "uuid",
      "insight_type": "priority_reasoning",
      "title": "High Priority Task",
      "summary": "This task blocks 3 other critical tasks",
      "confidence_score": 0.87,
      "impact_score": 0.92,
      "reasoning_path": [
        {
          "level": "pillar",
          "entity_name": "Career",
          "reasoning": "Aligns with career advancement goals",
          "confidence": 0.9
        }
      ],
      "user_feedback": null,
      "created_at": "2025-01-20T10:00:00Z"
    }
  ]
}
```

### POST `/api/insights/{entity_type}/{entity_id}/analyze`
Trigger HRM analysis for an entity.

**Path Parameters:**
- `entity_type`: One of `pillar`, `area`, `project`, `task`
- `entity_id`: UUID of the entity

**Query Parameters:**
- `analysis_depth`: One of `minimal`, `balanced`, `detailed` (default: balanced)

**Response 202:**
```json
{
  "message": "Analysis initiated",
  "analysis_id": "uuid",
  "estimated_completion": "2025-01-20T10:00:05Z"
}
```

### POST `/api/insights/{insight_id}/feedback`
Submit feedback on an insight.

**Path Parameters:**
- `insight_id`: UUID of the insight

**Query Parameters:**
- `feedback`: One of `accepted`, `rejected`, `modified`, `ignored`

**Request Body (optional):**
```json
{
  "feedback_text": "The reasoning was helpful but priority seems too high",
  "suggested_improvement": "Consider deadline proximity more heavily"
}
```

**Response 200:**
```json
{
  "status": "feedback recorded",
  "insight_id": "uuid"
}
```

---

## 📊 Core PAPT Hierarchy Endpoints

### GET `/api/pillars`
Get all pillars for the authenticated user.

**Query Parameters:**
- `include_archived` (optional): Include archived pillars (default: false)
- `include_stats` (optional): Include statistics (default: true)

**Response 200:**
```json
{
  "pillars": [
    {
      "id": "uuid",
      "name": "Career",
      "description": "Professional growth and development",
      "icon": "💼",
      "color": "#3B82F6",
      "time_allocation_percentage": 40,
      "sort_order": 1,
      "archived": false,
      "created_at": "2025-01-01T00:00:00Z",
      "stats": {
        "areas_count": 3,
        "projects_count": 7,
        "tasks_count": 42,
        "completion_percentage": 65
      }
    }
  ]
}
```

### POST `/api/pillars`
Create a new pillar.

**Request Body:**
```json
{
  "name": "Health & Wellness",
  "description": "Physical and mental wellbeing",
  "icon": "🏃",
  "color": "#10B981",
  "time_allocation_percentage": 30
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "name": "Health & Wellness",
  "created_at": "2025-01-20T10:00:00Z"
}
```

### PUT `/api/pillars/{pillar_id}`
Update an existing pillar.

**Path Parameters:**
- `pillar_id`: UUID of the pillar

**Request Body:**
```json
{
  "name": "Updated Name",
  "time_allocation_percentage": 35
}
```

### DELETE `/api/pillars/{pillar_id}`
Delete a pillar (cascade deletes areas, projects, and tasks).

**Path Parameters:**
- `pillar_id`: UUID of the pillar

**Response 204:** No content

---

## 📈 Today/Priority Endpoints

### GET `/api/today`
Get prioritized tasks for today with AI analysis.

**Query Parameters:**
- `coaching_top_n` (optional): Number of tasks to include AI coaching (default: 3)
- `use_hrm` (optional): Use Hierarchical Reasoning Model (default: true)

**Response 200:**
```json
{
  "date": "2025-01-20T10:00:00Z",
  "tasks": [
    {
      "id": "uuid",
      "name": "Complete project proposal",
      "hrm_priority_score": 87.5,
      "hrm_reasoning_summary": "Critical for MVP launch deadline",
      "hrm_analysis": {
        "primary_factors": ["deadline_proximity", "blocker_count"],
        "confidence": 0.89
      },
      "due_date": "2025-01-20T17:00:00Z",
      "project_name": "MVP Launch",
      "area_name": "Product Development",
      "pillar_name": "Career"
    }
  ],
  "hrm_enabled": true,
  "analysis_method": "hierarchical_reasoning_model"
}
```

### POST `/api/today/plan`
Generate AI-powered daily plan.

**Request Body:**
```json
{
  "energy_level": "high",
  "available_hours": 6,
  "focus_areas": ["deep_work", "collaboration"]
}
```

**Response 200:**
```json
{
  "schedule": [
    {
      "time_block": "09:00-10:30",
      "task_id": "uuid",
      "task_name": "Write technical documentation",
      "reasoning": "Matches high energy with deep work requirement",
      "estimated_duration": 90
    }
  ],
  "ai_notes": "Scheduled most cognitively demanding tasks during peak hours"
}
```

---

## 🔍 Search Endpoints

### GET `/api/search`
Search across all entities.

**Query Parameters:**
- `q`: Search query (required)
- `types` (optional): Comma-separated entity types to search
- `limit` (optional): Maximum results per type (default: 10)

**Response 200:**
```json
{
  "results": {
    "tasks": [
      {
        "id": "uuid",
        "name": "Task matching query",
        "type": "task",
        "highlight": "Task <mark>matching</mark> query"
      }
    ],
    "projects": [],
    "areas": [],
    "pillars": []
  },
  "total_count": 1
}
```

---

## 📊 Analytics Endpoints

### GET `/api/analytics/alignment-snapshot`
Get current alignment snapshot.

**Response 200:**
```json
{
  "alignment_score": 78,
  "monthly_progress": 12,
  "pillar_distribution": [
    {
      "pillar_name": "Career",
      "percentage": 45,
      "target_percentage": 40,
      "task_count": 28
    }
  ],
  "recommendations": [
    "Consider reducing Career focus by 5% to match target allocation"
  ]
}
```

---

## 🛠️ Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

### Common Error Codes:
- `AUTHENTICATION_REQUIRED`: Missing or invalid token
- `PERMISSION_DENIED`: User lacks access to resource
- `NOT_FOUND`: Resource doesn't exist
- `VALIDATION_ERROR`: Request validation failed
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error

---

## 📉 Rate Limiting

- **Authenticated requests**: 1000 per hour
- **AI analysis requests**: 100 per hour
- **Unauthenticated requests**: 60 per hour

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642680000
```

---

## 🔄 Versioning

The API uses URL versioning. Current version is v1. Future versions will be accessible at `/api/v2/`.

Breaking changes will be announced 30 days in advance with migration guides.

---

## 📚 Additional Resources

- **Postman Collection**: [Download](https://api.aurumlife.com/docs/postman)
- **OpenAPI Spec**: [View](https://api.aurumlife.com/openapi.json)
- **Status Page**: [status.aurumlife.com](https://status.aurumlife.com)
- **Support**: api-support@aurumlife.com