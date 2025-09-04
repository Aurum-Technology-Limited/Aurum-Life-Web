"""
GraphQL Integration with FastAPI
Combines queries and mutations with authentication
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from typing import Optional, Dict, Any
import logging

from graphql_resolvers import Query
from graphql_mutations import Mutation
from models import User
from auth_bearer import JWTBearer
from fastapi import Depends

logger = logging.getLogger(__name__)

# Context getter for authentication
async def get_context(
    current_user: User = Depends(JWTBearer())
) -> Dict[str, Any]:
    """Get GraphQL context with authenticated user"""
    return {
        "user": current_user,
        "loaders": {}  # DataLoaders will be initialized per request
    }

# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        # Add any Strawberry extensions here
    ]
)

# Create GraphQL router
graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True,  # Enable GraphiQL interface in development
)

# Custom GraphQL configuration
graphql_config = {
    "debug": True,  # Set to False in production
    "introspection": True,  # Allow introspection queries
    "max_depth": 10,  # Maximum query depth to prevent abuse
    "max_complexity": 1000,  # Maximum query complexity
}

# Export for use in main server.py
__all__ = ['graphql_router', 'schema', 'graphql_config']