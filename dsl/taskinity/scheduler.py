"""
Task Scheduler for Taskinity.

This module provides functionality for scheduling flows to run at specific times
or intervals, with support for various scheduling patterns.
"""
import datetime
import json
import logging
import os
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, TypeVar

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False


class ScheduleType(Enum):
    """Types of schedules supported by the scheduler."""
    INTERVAL = "interval"  # Run every X minutes
    DAILY = "daily"        # Run at specific time(s) each day
    WEEKLY = "weekly"      # Run on specific day(s) of the week
    MONTHLY = "monthly"    # Run on specific day(s) of the month


class TaskScheduler:
    """Scheduler for Taskinity flows."""
    
    def __init__(
        self,
        storage_dir: str = "schedules",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the task scheduler.
        
        Args:
            storage_dir: Directory to store schedule definitions
            logger: Logger instance (optional)
        """
        if not SCHEDULE_AVAILABLE:
            raise ImportError("Schedule package is required for task scheduling. "
                             "Install with: pip install schedule")
        
        self.logger = logger or logging.getLogger(__name__)
        self.storage_dir = storage_dir
        self.schedules = {}
        self.running = False
        self.thread = None
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load existing schedules
        self._load_schedules()
    
    def _load_schedules(self) -> None:
        """Load existing schedules from storage directory."""
        self.logger.info(f"Loading schedules from {self.storage_dir}")
        
        schedule_files = Path(self.storage_dir).glob("*.json")
        for file_path in schedule_files:
            try:
                with open(file_path, "r") as f:
                    schedule_data = json.load(f)
                
                schedule_id = file_path.stem
                self.schedules[schedule_id] = schedule_data
                self.logger.info(f"Loaded schedule {schedule_id}")
            
            except Exception as e:
                self.logger.error(f"Error loading schedule from {file_path}: {str(e)}")
    
    def _save_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]) -> None:
        """
        Save schedule to storage directory.
        
        Args:
            schedule_id: Schedule ID
            schedule_data: Schedule data
        """
        file_path = Path(self.storage_dir) / f"{schedule_id}.json"
        
        try:
            with open(file_path, "w") as f:
                json.dump(schedule_data, f, indent=2)
            
            self.logger.info(f"Saved schedule {schedule_id}")
        
        except Exception as e:
            self.logger.error(f"Error saving schedule {schedule_id}: {str(e)}")
    
    def _delete_schedule_file(self, schedule_id: str) -> None:
        """
        Delete schedule file from storage directory.
        
        Args:
            schedule_id: Schedule ID
        """
        file_path = Path(self.storage_dir) / f"{schedule_id}.json"
        
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Deleted schedule file for {schedule_id}")
        
        except Exception as e:
            self.logger.error(f"Error deleting schedule file for {schedule_id}: {str(e)}")
    
    def create_schedule(
        self,
        flow_path: str,
        schedule_type: ScheduleType,
        schedule_params: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Create a new schedule.
        
        Args:
            flow_path: Path to the flow DSL file
            schedule_type: Type of schedule
            schedule_params: Parameters for the schedule type
            input_data: Input data for the flow (optional)
            name: Schedule name (optional)
            description: Schedule description (optional)
            
        Returns:
            Schedule ID
        """
        # Validate flow path
        if not os.path.exists(flow_path):
            raise ValueError(f"Flow file not found: {flow_path}")
        
        # Generate schedule ID
        schedule_id = f"schedule_{int(time.time())}_{os.path.basename(flow_path)}"
        
        # Create schedule data
        schedule_data = {
            "flow_path": flow_path,
            "schedule_type": schedule_type.value,
            "schedule_params": schedule_params,
            "input_data": input_data or {},
            "name": name or os.path.basename(flow_path),
            "description": description or f"Schedule for {os.path.basename(flow_path)}",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "last_run": None,
            "next_run": None,
            "enabled": True
        }
        
        # Save schedule
        self.schedules[schedule_id] = schedule_data
        self._save_schedule(schedule_id, schedule_data)
        
        # Register schedule if scheduler is running
        if self.running:
            self._register_schedule(schedule_id, schedule_data)
        
        self.logger.info(f"Created schedule {schedule_id}")
        return schedule_id
    
    def update_schedule(
        self,
        schedule_id: str,
        schedule_type: Optional[ScheduleType] = None,
        schedule_params: Optional[Dict[str, Any]] = None,
        input_data: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        enabled: Optional[bool] = None
    ) -> None:
        """
        Update an existing schedule.
        
        Args:
            schedule_id: Schedule ID
            schedule_type: Type of schedule (optional)
            schedule_params: Parameters for the schedule type (optional)
            input_data: Input data for the flow (optional)
            name: Schedule name (optional)
            description: Schedule description (optional)
            enabled: Whether the schedule is enabled (optional)
        """
        if schedule_id not in self.schedules:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        schedule_data = self.schedules[schedule_id]
        
        # Update schedule data
        if schedule_type is not None:
            schedule_data["schedule_type"] = schedule_type.value
        
        if schedule_params is not None:
            schedule_data["schedule_params"] = schedule_params
        
        if input_data is not None:
            schedule_data["input_data"] = input_data
        
        if name is not None:
            schedule_data["name"] = name
        
        if description is not None:
            schedule_data["description"] = description
        
        if enabled is not None:
            schedule_data["enabled"] = enabled
        
        schedule_data["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save schedule
        self._save_schedule(schedule_id, schedule_data)
        
        # Re-register schedule if scheduler is running
        if self.running:
            # Clear existing schedule
            schedule.clear(schedule_id)
            
            # Register schedule if enabled
            if schedule_data.get("enabled", True):
                self._register_schedule(schedule_id, schedule_data)
        
        self.logger.info(f"Updated schedule {schedule_id}")
    
    def delete_schedule(self, schedule_id: str) -> None:
        """
        Delete a schedule.
        
        Args:
            schedule_id: Schedule ID
        """
        if schedule_id not in self.schedules:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        # Clear schedule if scheduler is running
        if self.running:
            schedule.clear(schedule_id)
        
        # Delete schedule
        del self.schedules[schedule_id]
        self._delete_schedule_file(schedule_id)
        
        self.logger.info(f"Deleted schedule {schedule_id}")
    
    def get_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """
        Get schedule data.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Schedule data
        """
        if schedule_id not in self.schedules:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        return self.schedules[schedule_id]
    
    def list_schedules(self) -> List[Dict[str, Any]]:
        """
        List all schedules.
        
        Returns:
            List of schedules
        """
        return [
            {"id": schedule_id, **schedule_data}
            for schedule_id, schedule_data in self.schedules.items()
        ]
    
    def run_schedule(self, schedule_id: str) -> Any:
        """
        Run a schedule immediately.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Result of the flow execution
        """
        if schedule_id not in self.schedules:
            raise ValueError(f"Schedule not found: {schedule_id}")
        
        schedule_data = self.schedules[schedule_id]
        
        # Import here to avoid circular imports
        from taskinity import run_flow_from_dsl, load_dsl
        
        # Load flow DSL
        flow_path = schedule_data["flow_path"]
        flow_dsl = load_dsl(flow_path)
        
        # Run flow
        self.logger.info(f"Running schedule {schedule_id}")
        
        try:
            result = run_flow_from_dsl(flow_dsl, schedule_data["input_data"])
            
            # Update last run time
            schedule_data["last_run"] = datetime.datetime.now().isoformat()
            self._save_schedule(schedule_id, schedule_data)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error running schedule {schedule_id}: {str(e)}")
            raise
    
    def start(self) -> None:
        """Start the scheduler."""
        if self.running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.logger.info("Starting scheduler")
        
        # Register all enabled schedules
        for schedule_id, schedule_data in self.schedules.items():
            if schedule_data.get("enabled", True):
                self._register_schedule(schedule_id, schedule_data)
        
        # Start scheduler in a separate thread
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if not self.running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.logger.info("Stopping scheduler")
        
        # Clear all schedules
        schedule.clear()
        
        # Stop scheduler
        self.running = False
        
        # Wait for thread to finish
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None
    
    def _run_scheduler(self) -> None:
        """Run the scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _register_schedule(self, schedule_id: str, schedule_data: Dict[str, Any]) -> None:
        """
        Register a schedule with the scheduler.
        
        Args:
            schedule_id: Schedule ID
            schedule_data: Schedule data
        """
        schedule_type = schedule_data["schedule_type"]
        schedule_params = schedule_data["schedule_params"]
        
        # Create job function
        def job():
            try:
                self.run_schedule(schedule_id)
            except Exception as e:
                self.logger.error(f"Error running schedule {schedule_id}: {str(e)}")
        
        # Register job based on schedule type
        if schedule_type == ScheduleType.INTERVAL.value:
            minutes = schedule_params.get("minutes", 60)
            job_schedule = schedule.every(minutes).minutes
            job_schedule.do(job).tag(schedule_id)
            
            # Calculate next run time
            next_run = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            schedule_data["next_run"] = next_run.isoformat()
        
        elif schedule_type == ScheduleType.DAILY.value:
            time_str = schedule_params.get("time", "00:00")
            job_schedule = schedule.every().day.at(time_str)
            job_schedule.do(job).tag(schedule_id)
            
            # Calculate next run time
            hour, minute = map(int, time_str.split(":"))
            next_run = datetime.datetime.now().replace(hour=hour, minute=minute)
            if next_run < datetime.datetime.now():
                next_run += datetime.timedelta(days=1)
            schedule_data["next_run"] = next_run.isoformat()
        
        elif schedule_type == ScheduleType.WEEKLY.value:
            day = schedule_params.get("day", "monday")
            time_str = schedule_params.get("time", "00:00")
            
            # Get day of week method
            day_method = getattr(schedule.every(), day.lower())
            job_schedule = day_method.at(time_str)
            job_schedule.do(job).tag(schedule_id)
            
            # Calculate next run time
            hour, minute = map(int, time_str.split(":"))
            weekday = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                      "friday": 4, "saturday": 5, "sunday": 6}[day.lower()]
            
            next_run = datetime.datetime.now().replace(hour=hour, minute=minute)
            days_ahead = weekday - next_run.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_run += datetime.timedelta(days=days_ahead)
            schedule_data["next_run"] = next_run.isoformat()
        
        elif schedule_type == ScheduleType.MONTHLY.value:
            day = schedule_params.get("day", 1)
            time_str = schedule_params.get("time", "00:00")
            
            # Register job using a custom function
            def monthly_job():
                now = datetime.datetime.now()
                target_day = day
                
                # Adjust for months with fewer days
                month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if now.month == 2 and now.year % 4 == 0 and (now.year % 100 != 0 or now.year % 400 == 0):
                    month_days[1] = 29
                
                if target_day > month_days[now.month - 1]:
                    target_day = month_days[now.month - 1]
                
                target_date = now.replace(day=target_day)
                hour, minute = map(int, time_str.split(":"))
                target_time = target_date.replace(hour=hour, minute=minute)
                
                if target_time > now:
                    # Run today
                    seconds_until = (target_time - now).total_seconds()
                    threading.Timer(seconds_until, job).start()
                else:
                    # Run next month
                    next_month = now.month + 1
                    next_year = now.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    
                    # Adjust for months with fewer days
                    target_day = day
                    if target_day > month_days[next_month - 1]:
                        target_day = month_days[next_month - 1]
                    
                    next_run = datetime.datetime(next_year, next_month, target_day, hour, minute)
                    seconds_until = (next_run - now).total_seconds()
                    threading.Timer(seconds_until, job).start()
                    
                    # Update next run time in schedule data
                    schedule_data["next_run"] = next_run.isoformat()
                    self._save_schedule(schedule_id, schedule_data)
            
            # Run monthly job
            monthly_job()
        
        else:
            self.logger.error(f"Unknown schedule type: {schedule_type}")
        
        # Save updated schedule data
        self._save_schedule(schedule_id, schedule_data)


class ScheduleManager:
    """Command-line interface for managing schedules."""
    
    def __init__(self, storage_dir: str = "schedules"):
        """
        Initialize the schedule manager.
        
        Args:
            storage_dir: Directory to store schedule definitions
        """
        self.scheduler = TaskScheduler(storage_dir=storage_dir)
    
    def start(self) -> None:
        """Start the scheduler."""
        self.scheduler.start()
        print("Scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.stop()
        print("Scheduler stopped")
    
    def create(
        self,
        flow_path: str,
        interval: Optional[int] = None,
        daily_time: Optional[str] = None,
        weekly_day: Optional[str] = None,
        weekly_time: Optional[str] = None,
        monthly_day: Optional[int] = None,
        monthly_time: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Create a new schedule.
        
        Args:
            flow_path: Path to the flow DSL file
            interval: Run every X minutes (for interval schedule)
            daily_time: Time to run (for daily schedule, format: HH:MM)
            weekly_day: Day of week (for weekly schedule)
            weekly_time: Time to run (for weekly schedule, format: HH:MM)
            monthly_day: Day of month (for monthly schedule)
            monthly_time: Time to run (for monthly schedule, format: HH:MM)
            name: Schedule name (optional)
            description: Schedule description (optional)
        """
        # Determine schedule type and parameters
        if interval is not None:
            schedule_type = ScheduleType.INTERVAL
            schedule_params = {"minutes": interval}
        elif daily_time is not None:
            schedule_type = ScheduleType.DAILY
            schedule_params = {"time": daily_time}
        elif weekly_day is not None:
            schedule_type = ScheduleType.WEEKLY
            schedule_params = {"day": weekly_day, "time": weekly_time or "00:00"}
        elif monthly_day is not None:
            schedule_type = ScheduleType.MONTHLY
            schedule_params = {"day": monthly_day, "time": monthly_time or "00:00"}
        else:
            print("Error: No schedule parameters provided")
            return
        
        # Create schedule
        try:
            schedule_id = self.scheduler.create_schedule(
                flow_path=flow_path,
                schedule_type=schedule_type,
                schedule_params=schedule_params,
                name=name,
                description=description
            )
            print(f"Created schedule: {schedule_id}")
        
        except Exception as e:
            print(f"Error creating schedule: {str(e)}")
    
    def list(self) -> None:
        """List all schedules."""
        schedules = self.scheduler.list_schedules()
        
        if not schedules:
            print("No schedules found")
            return
        
        print(f"Found {len(schedules)} schedules:")
        for schedule in schedules:
            enabled = "Enabled" if schedule.get("enabled", True) else "Disabled"
            print(f"- {schedule['id']} ({enabled}): {schedule['name']}")
            print(f"  Flow: {schedule['flow_path']}")
            print(f"  Type: {schedule['schedule_type']}")
            print(f"  Last run: {schedule.get('last_run', 'Never')}")
            print(f"  Next run: {schedule.get('next_run', 'Not scheduled')}")
            print()
    
    def run(self, schedule_id: str) -> None:
        """
        Run a schedule immediately.
        
        Args:
            schedule_id: Schedule ID
        """
        try:
            self.scheduler.run_schedule(schedule_id)
            print(f"Schedule {schedule_id} executed successfully")
        
        except Exception as e:
            print(f"Error running schedule: {str(e)}")
    
    def delete(self, schedule_id: str) -> None:
        """
        Delete a schedule.
        
        Args:
            schedule_id: Schedule ID
        """
        try:
            self.scheduler.delete_schedule(schedule_id)
            print(f"Deleted schedule: {schedule_id}")
        
        except Exception as e:
            print(f"Error deleting schedule: {str(e)}")
    
    def enable(self, schedule_id: str) -> None:
        """
        Enable a schedule.
        
        Args:
            schedule_id: Schedule ID
        """
        try:
            self.scheduler.update_schedule(schedule_id, enabled=True)
            print(f"Enabled schedule: {schedule_id}")
        
        except Exception as e:
            print(f"Error enabling schedule: {str(e)}")
    
    def disable(self, schedule_id: str) -> None:
        """
        Disable a schedule.
        
        Args:
            schedule_id: Schedule ID
        """
        try:
            self.scheduler.update_schedule(schedule_id, enabled=False)
            print(f"Disabled schedule: {schedule_id}")
        
        except Exception as e:
            print(f"Error disabling schedule: {str(e)}")


def main():
    """Command-line entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Taskinity Schedule Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Start scheduler
    start_parser = subparsers.add_parser("start", help="Start the scheduler")
    
    # Stop scheduler
    stop_parser = subparsers.add_parser("stop", help="Stop the scheduler")
    
    # Create schedule
    create_parser = subparsers.add_parser("create", help="Create a new schedule")
    create_parser.add_argument("flow_path", help="Path to the flow DSL file")
    create_parser.add_argument("--interval", type=int, help="Run every X minutes")
    create_parser.add_argument("--daily-time", help="Time to run (format: HH:MM)")
    create_parser.add_argument("--weekly-day", help="Day of week")
    create_parser.add_argument("--weekly-time", help="Time to run (format: HH:MM)")
    create_parser.add_argument("--monthly-day", type=int, help="Day of month")
    create_parser.add_argument("--monthly-time", help="Time to run (format: HH:MM)")
    create_parser.add_argument("--name", help="Schedule name")
    create_parser.add_argument("--description", help="Schedule description")
    
    # List schedules
    list_parser = subparsers.add_parser("list", help="List all schedules")
    
    # Run schedule
    run_parser = subparsers.add_parser("run", help="Run a schedule immediately")
    run_parser.add_argument("schedule_id", help="Schedule ID")
    
    # Delete schedule
    delete_parser = subparsers.add_parser("delete", help="Delete a schedule")
    delete_parser.add_argument("schedule_id", help="Schedule ID")
    
    # Enable schedule
    enable_parser = subparsers.add_parser("enable", help="Enable a schedule")
    enable_parser.add_argument("schedule_id", help="Schedule ID")
    
    # Disable schedule
    disable_parser = subparsers.add_parser("disable", help="Disable a schedule")
    disable_parser.add_argument("schedule_id", help="Schedule ID")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create schedule manager
    manager = ScheduleManager()
    
    # Run command
    if args.command == "start":
        manager.start()
    elif args.command == "stop":
        manager.stop()
    elif args.command == "create":
        manager.create(
            flow_path=args.flow_path,
            interval=args.interval,
            daily_time=args.daily_time,
            weekly_day=args.weekly_day,
            weekly_time=args.weekly_time,
            monthly_day=args.monthly_day,
            monthly_time=args.monthly_time,
            name=args.name,
            description=args.description
        )
    elif args.command == "list":
        manager.list()
    elif args.command == "run":
        manager.run(args.schedule_id)
    elif args.command == "delete":
        manager.delete(args.schedule_id)
    elif args.command == "enable":
        manager.enable(args.schedule_id)
    elif args.command == "disable":
        manager.disable(args.schedule_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
