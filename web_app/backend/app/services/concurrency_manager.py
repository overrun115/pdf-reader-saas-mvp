import asyncio
import time
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class Task:
    id: str
    file_id: str
    filename: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    timeout_seconds: int = 300  # 5 minutes default timeout

class ConcurrencyManager:
    """Manages concurrent PDF processing with queuing and limits."""
    
    def __init__(self, max_concurrent_tasks: int = 3, max_queue_size: int = 50):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_queue_size = max_queue_size
        self.tasks: Dict[str, Task] = {}
        self.queue: List[str] = []  # Task IDs in queue
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        
    async def submit_task(
        self, 
        file_id: str, 
        filename: str, 
        processor_func: Callable,
        timeout_seconds: int = 300
    ) -> str:
        """Submit a new task for processing."""
        
        async with self._lock:
            # Check queue size
            if len(self.queue) + len(self.running_tasks) >= self.max_queue_size:
                raise Exception(f"Queue is full (max {self.max_queue_size} tasks)")
            
            # Create new task
            task_id = str(uuid.uuid4())
            task = Task(
                id=task_id,
                file_id=file_id,
                filename=filename,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                timeout_seconds=timeout_seconds
            )
            
            self.tasks[task_id] = task
            self.queue.append(task_id)
            
            logger.info(f"Task {task_id} queued for file {filename}")
            
            # Try to start processing
            await self._process_queue(processor_func)
            
            return task_id
    
    async def _process_queue(self, processor_func: Callable):
        """Process tasks from queue if slots available."""
        
        while (len(self.running_tasks) < self.max_concurrent_tasks and 
               len(self.queue) > 0):
            
            task_id = self.queue.pop(0)
            task = self.tasks[task_id]
            
            # Start processing
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            # Create asyncio task
            async_task = asyncio.create_task(
                self._run_task_with_timeout(task, processor_func)
            )
            self.running_tasks[task_id] = async_task
            
            logger.info(f"Started processing task {task_id} ({task.filename})")
    
    async def _run_task_with_timeout(self, task: Task, processor_func: Callable):
        """Run a single task with timeout handling."""
        
        try:
            # Run with timeout
            result = await asyncio.wait_for(
                processor_func(task.file_id, task.filename),
                timeout=task.timeout_seconds
            )
            
            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            logger.info(f"Task {task.id} completed successfully")
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.completed_at = datetime.now()
            task.error = f"Task timed out after {task.timeout_seconds} seconds"
            logger.warning(f"Task {task.id} timed out")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = str(e)
            logger.error(f"Task {task.id} failed: {e}")
            
        finally:
            # Remove from running tasks
            async with self._lock:
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]
            
            # Try to process more from queue (without lock to avoid deadlock)
            try:
                await self._process_queue(processor_func)
            except Exception as e:
                logger.error(f"Error processing queue after task completion: {e}")
    
    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get status of a specific task."""
        return self.tasks.get(task_id)
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status."""
        async with self._lock:
            return {
                "queue_length": len(self.queue),
                "running_tasks": len(self.running_tasks),
                "max_concurrent": self.max_concurrent_tasks,
                "max_queue_size": self.max_queue_size,
                "total_tasks": len(self.tasks),
                "pending_tasks": [task_id for task_id in self.queue],
                "running_task_ids": list(self.running_tasks.keys())
            }
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Clean up old completed/failed tasks."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT] and
                task.completed_at and task.completed_at < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
            logger.info(f"Cleaned up old task {task_id}")
        
        return len(tasks_to_remove)

# Global instance
pdf_concurrency_manager = ConcurrencyManager(
    max_concurrent_tasks=3,  # Process max 3 PDFs simultaneously
    max_queue_size=20        # Allow max 20 PDFs in queue
)