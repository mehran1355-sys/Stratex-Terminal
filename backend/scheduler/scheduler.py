"""
مدیریت وظایف زمان‌بندی شده
Task Scheduler
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScheduledTask:
    task_id: str
    name: str
    description: str
    func: Callable
    trigger_type: str
    trigger_config: Dict
    status: TaskStatus = TaskStatus.PENDING
    last_run: Optional[datetime] = None
    run_count: int = 0
    error_count: int = 0
    is_enabled: bool = True
    timeout_seconds: int = 300


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.tasks: Dict[str, ScheduledTask] = {}
        self._setup_default_tasks()

    def _setup_default_tasks(self):
        self.add_task(ScheduledTask("daily_analysis", "تحلیل روزانه", "تحلیل همه نمادها", self._dummy_func, "cron", {"hour": 0, "minute": 5}))
        self.add_task(ScheduledTask("weekly_analysis", "تحلیل هفتگی", "تحلیل هفتگی", self._dummy_func, "cron", {"day_of_week": "fri", "hour": 23, "minute": 0}))
        self.add_task(ScheduledTask("monthly_analysis", "تحلیل ماهانه", "تحلیل ماهانه", self._dummy_func, "cron", {"day": "last", "hour": 23, "minute": 0}))
        self.add_task(ScheduledTask("daily_report", "گزارش روزانه", "تولید گزارش", self._dummy_func, "cron", {"hour": 23, "minute": 30}))
        self.add_task(ScheduledTask("check_tp_sl", "بررسی TP/SL", "چک معاملات", self._dummy_func, "interval", {"seconds": 10}))
        self.add_task(ScheduledTask("health_check", "Health Check", "سلامت سرور", self._dummy_func, "interval", {"seconds": 30}))

    def add_task(self, task: ScheduledTask):
        self.tasks[task.task_id] = task

    def register_handler(self, task_id: str, handler: Callable):
        if task_id in self.tasks:
            self.tasks[task_id].func = handler

    async def start(self):
        for task_id, task in self.tasks.items():
            if not task.is_enabled:
                continue
            trigger = CronTrigger(**task.trigger_config) if task.trigger_type == "cron" else IntervalTrigger(**task.trigger_config)
            self.scheduler.add_job(self._execute_task, trigger, args=[task_id], id=task_id, name=task.name, max_instances=1, coalesce=True)
        self.scheduler.start()
        logger.info(f"✅ Scheduler started with {len(self.tasks)} tasks")

    async def stop(self):
        self.scheduler.shutdown(wait=False)

    async def _execute_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()
        task.run_count += 1
        try:
            if asyncio.iscoroutinefunction(task.func):
                await asyncio.wait_for(task.func(), timeout=task.timeout_seconds)
            else:
                await asyncio.get_event_loop().run_in_executor(None, task.func)
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_count += 1
            logger.error(f"Task {task.name} failed: {e}")

    def get_status(self) -> List[Dict]:
        return [{"task_id": t.task_id, "name": t.name, "status": t.status.value, "last_run": t.last_run.isoformat() if t.last_run else None, "run_count": t.run_count} for t in self.tasks.values()]

    def toggle_task(self, task_id: str, enabled: bool):
        if task_id in self.tasks:
            self.tasks[task_id].is_enabled = enabled
            self.scheduler.resume_job(task_id) if enabled else self.scheduler.pause_job(task_id)

    async def _dummy_func(self):
        pass


task_scheduler = TaskScheduler()
