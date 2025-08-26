"""
Base Agent Framework for Aurum Life Multi-Agent System
Provides foundational infrastructure for all agents
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from pydantic import BaseModel, Field
from celery import Task
from celery_app import app
import json

logger = logging.getLogger(__name__)

class AgentState(str, Enum):
    """Agent lifecycle states"""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"

class AgentMessage(BaseModel):
    """Standard message format for inter-agent communication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_agent: str
    target_agent: str
    message_type: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=5, ge=1, le=10)

class AgentCapability(BaseModel):
    """Defines what an agent can do"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    
class BaseAgent(ABC):
    """
    Abstract base class for all Aurum Life agents
    Provides standard interfaces and common functionality
    """
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = AgentState.INITIALIZING
        self.capabilities: List[AgentCapability] = []
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.context: Dict[str, Any] = {}
        self._handlers: Dict[str, callable] = {}
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources and connections"""
        pass
        
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming message and optionally return response"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of agent capabilities"""
        pass
        
    async def start(self) -> None:
        """Start the agent's main processing loop"""
        try:
            await self.initialize()
            self.state = AgentState.READY
            logger.info(f"Agent {self.agent_id} ({self.agent_type}) started successfully")
            
            # Main message processing loop
            while self.state not in [AgentState.ERROR, AgentState.TERMINATED]:
                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(
                        self.message_queue.get(), 
                        timeout=30.0
                    )
                    
                    self.state = AgentState.PROCESSING
                    response = await self.process_message(message)
                    
                    if response:
                        await self.send_message(response)
                        
                    self.state = AgentState.READY
                    
                except asyncio.TimeoutError:
                    # No messages, continue loop
                    continue
                    
                except Exception as e:
                    logger.error(f"Error processing message in agent {self.agent_id}: {e}")
                    self.state = AgentState.ERROR
                    
        except Exception as e:
            logger.error(f"Fatal error in agent {self.agent_id}: {e}")
            self.state = AgentState.ERROR
            
    async def send_message(self, message: AgentMessage) -> None:
        """Send message to another agent via Celery"""
        route_message.delay(message.dict())
        
    async def receive_message(self, message: AgentMessage) -> None:
        """Receive message from another agent"""
        await self.message_queue.put(message)
        
    def register_handler(self, message_type: str, handler: callable) -> None:
        """Register a handler for specific message type"""
        self._handlers[message_type] = handler
        
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Route message to appropriate handler"""
        handler = self._handlers.get(message.message_type)
        if handler:
            return await handler(message)
        else:
            logger.warning(f"No handler for message type {message.message_type} in agent {self.agent_id}")
            return None
            
    def update_state(self, new_state: AgentState) -> None:
        """Update agent state with logging"""
        old_state = self.state
        self.state = new_state
        logger.info(f"Agent {self.agent_id} state changed: {old_state} -> {new_state}")
        
    def add_capability(self, capability: AgentCapability) -> None:
        """Register a new capability"""
        self.capabilities.append(capability)
        
    async def shutdown(self) -> None:
        """Gracefully shutdown the agent"""
        logger.info(f"Shutting down agent {self.agent_id}")
        self.state = AgentState.TERMINATED

# Celery task for routing messages between agents
@app.task(name='agent_base.route_message')
def route_message(message_dict: Dict[str, Any]) -> None:
    """Route messages between agents using Celery"""
    message = AgentMessage(**message_dict)
    
    # Route to specific agent queue
    app.send_task(
        f'agents.{message.target_agent}.receive_message',
        args=[message_dict],
        queue=f'agent_{message.target_agent}',
        priority=message.priority
    )
    
    logger.info(f"Routed message {message.id} from {message.source_agent} to {message.target_agent}")

class AgentOrchestrator:
    """
    Central orchestrator for managing all agents
    Implements the choreography pattern for agent coordination
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, List[str]] = {}
        self.event_log: List[AgentMessage] = []
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent {agent.agent_id} of type {agent.agent_type}")
        
    def define_workflow(self, workflow_id: str, agent_sequence: List[str]) -> None:
        """Define a workflow as a sequence of agents"""
        self.workflows[workflow_id] = agent_sequence
        
    async def execute_workflow(self, workflow_id: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a predefined workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_id}")
            
        agent_sequence = self.workflows[workflow_id]
        correlation_id = str(uuid.uuid4())
        current_data = initial_data
        
        for agent_id in agent_sequence:
            if agent_id not in self.agents:
                raise ValueError(f"Unknown agent in workflow: {agent_id}")
                
            # Create message for agent
            message = AgentMessage(
                source_agent="orchestrator",
                target_agent=agent_id,
                message_type="workflow_task",
                payload=current_data,
                correlation_id=correlation_id
            )
            
            # Send to agent and wait for response
            response = await self.agents[agent_id].process_message(message)
            
            if response:
                current_data = response.payload
                self.event_log.append(response)
            else:
                logger.error(f"No response from agent {agent_id} in workflow {workflow_id}")
                break
                
        return current_data
        
    def get_agent_status(self) -> Dict[str, str]:
        """Get current status of all agents"""
        return {
            agent_id: agent.state.value 
            for agent_id, agent in self.agents.items()
        }