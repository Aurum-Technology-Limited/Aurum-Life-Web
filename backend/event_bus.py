"""
Event Bus Service for Multi-Agent Communication
Uses Redis Streams for reliable, distributed event streaming
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import redis.asyncio as redis
from contextlib import asynccontextmanager
import os

logger = logging.getLogger(__name__)

class EventBus:
    """
    Centralized event bus for agent communication
    Implements pub/sub pattern with Redis Streams for reliability
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client: Optional[redis.Redis] = None
        self.subscribers: Dict[str, List[Callable]] = {}
        self.consumer_groups: Dict[str, str] = {}
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
    async def connect(self) -> None:
        """Establish Redis connection"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                decode_responses=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            logger.info("Event bus connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
            
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            
    @asynccontextmanager
    async def connection(self):
        """Context manager for Redis connection"""
        await self.connect()
        try:
            yield self
        finally:
            await self.disconnect()
            
    async def publish_event(
        self, 
        stream_name: str, 
        event_type: str, 
        data: Dict[str, Any],
        source_agent: Optional[str] = None,
        target_agent: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Publish event to Redis stream
        
        Args:
            stream_name: Name of the stream (e.g., 'agent_events')
            event_type: Type of event (e.g., 'hypothesis_validated')
            data: Event payload
            source_agent: ID of agent publishing the event
            target_agent: ID of target agent (optional)
            correlation_id: For tracking related events
            
        Returns:
            Event ID from Redis
        """
        if not self.redis_client:
            raise RuntimeError("Event bus not connected")
            
        event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'source_agent': source_agent or 'system',
            'data': json.dumps(data),
            'correlation_id': correlation_id or ''
        }
        
        if target_agent:
            event['target_agent'] = target_agent
            
        # Publish to stream
        event_id = await self.redis_client.xadd(
            stream_name,
            event,
            maxlen=10000  # Keep last 10k events
        )
        
        logger.debug(f"Published event {event_id} to {stream_name}: {event_type}")
        return event_id
        
    async def subscribe_to_stream(
        self,
        stream_name: str,
        consumer_group: str,
        consumer_name: str,
        handler: Callable,
        start_id: str = '>'
    ) -> None:
        """
        Subscribe to a Redis stream with consumer group
        
        Args:
            stream_name: Name of the stream
            consumer_group: Consumer group name
            consumer_name: Unique consumer name
            handler: Async function to handle events
            start_id: Where to start reading ('>' for new messages only)
        """
        if not self.redis_client:
            raise RuntimeError("Event bus not connected")
            
        # Create consumer group if it doesn't exist
        try:
            await self.redis_client.xgroup_create(
                stream_name, 
                consumer_group, 
                id=start_id,
                mkstream=True
            )
            logger.info(f"Created consumer group {consumer_group} for {stream_name}")
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
                
        # Store subscription info
        key = f"{stream_name}:{consumer_group}:{consumer_name}"
        self.subscribers[key] = handler
        self.consumer_groups[key] = consumer_group
        
        # Start consumer task
        task = asyncio.create_task(
            self._consume_stream(stream_name, consumer_group, consumer_name, handler)
        )
        self._tasks.append(task)
        
    async def _consume_stream(
        self,
        stream_name: str,
        consumer_group: str,
        consumer_name: str,
        handler: Callable
    ) -> None:
        """Consume messages from stream"""
        logger.info(f"Starting consumer {consumer_name} for {stream_name}")
        
        while self._running:
            try:
                # Read messages with timeout
                messages = await self.redis_client.xreadgroup(
                    consumer_group,
                    consumer_name,
                    {stream_name: '>'},
                    count=10,
                    block=1000  # 1 second timeout
                )
                
                for stream, stream_messages in messages:
                    for message_id, data in stream_messages:
                        try:
                            # Parse event data
                            event = {
                                'id': message_id,
                                'stream': stream,
                                'event_type': data.get('event_type'),
                                'timestamp': data.get('timestamp'),
                                'source_agent': data.get('source_agent'),
                                'target_agent': data.get('target_agent'),
                                'correlation_id': data.get('correlation_id'),
                                'data': json.loads(data.get('data', '{}'))
                            }
                            
                            # Call handler
                            await handler(event)
                            
                            # Acknowledge message
                            await self.redis_client.xack(
                                stream_name,
                                consumer_group,
                                message_id
                            )
                            
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")
                            # Message will be redelivered after timeout
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in consumer {consumer_name}: {e}")
                await asyncio.sleep(5)  # Backoff on error
                
    async def start(self) -> None:
        """Start event bus consumers"""
        self._running = True
        logger.info("Event bus started")
        
    async def stop(self) -> None:
        """Stop event bus consumers"""
        self._running = False
        
        # Cancel all consumer tasks
        for task in self._tasks:
            task.cancel()
            
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        logger.info("Event bus stopped")
        
    async def get_pending_messages(
        self,
        stream_name: str,
        consumer_group: str
    ) -> List[Dict[str, Any]]:
        """Get pending messages for a consumer group"""
        if not self.redis_client:
            raise RuntimeError("Event bus not connected")
            
        pending = await self.redis_client.xpending(
            stream_name,
            consumer_group
        )
        
        return pending
        
    async def claim_abandoned_messages(
        self,
        stream_name: str,
        consumer_group: str,
        consumer_name: str,
        min_idle_time: int = 60000  # 60 seconds
    ) -> List[str]:
        """Claim messages abandoned by failed consumers"""
        if not self.redis_client:
            raise RuntimeError("Event bus not connected")
            
        # Get pending messages
        pending = await self.redis_client.xpending_range(
            stream_name,
            consumer_group,
            min='-',
            max='+',
            count=100
        )
        
        claimed_ids = []
        for msg in pending:
            if msg['time_since_delivered'] > min_idle_time:
                # Claim the message
                result = await self.redis_client.xclaim(
                    stream_name,
                    consumer_group,
                    consumer_name,
                    min_idle_time,
                    [msg['message_id']]
                )
                if result:
                    claimed_ids.append(msg['message_id'])
                    
        if claimed_ids:
            logger.info(f"Claimed {len(claimed_ids)} abandoned messages")
            
        return claimed_ids
        
    async def create_workflow_stream(self, workflow_id: str) -> str:
        """Create a dedicated stream for a workflow"""
        stream_name = f"workflow:{workflow_id}"
        
        # Initialize stream with metadata
        await self.publish_event(
            stream_name,
            'workflow_created',
            {
                'workflow_id': workflow_id,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        
        return stream_name
        
    async def get_workflow_events(
        self,
        workflow_id: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all events for a workflow"""
        if not self.redis_client:
            raise RuntimeError("Event bus not connected")
            
        stream_name = f"workflow:{workflow_id}"
        
        # Convert times to Redis IDs if provided
        start = start_time or '-'
        end = end_time or '+'
        
        # Read all events
        events = await self.redis_client.xrange(
            stream_name,
            min=start,
            max=end
        )
        
        # Parse events
        parsed_events = []
        for event_id, data in events:
            parsed_events.append({
                'id': event_id,
                'event_type': data.get('event_type'),
                'timestamp': data.get('timestamp'),
                'source_agent': data.get('source_agent'),
                'data': json.loads(data.get('data', '{}'))
            })
            
        return parsed_events

# Global event bus instance
event_bus = EventBus()

# Convenience functions
async def publish_agent_event(
    event_type: str,
    data: Dict[str, Any],
    source_agent: str,
    target_agent: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> str:
    """Publish an agent event to the main event stream"""
    return await event_bus.publish_event(
        'agent_events',
        event_type,
        data,
        source_agent,
        target_agent,
        correlation_id
    )

async def publish_workflow_event(
    workflow_id: str,
    event_type: str,
    data: Dict[str, Any],
    source_agent: str
) -> str:
    """Publish an event to a workflow-specific stream"""
    return await event_bus.publish_event(
        f"workflow:{workflow_id}",
        event_type,
        data,
        source_agent
    )