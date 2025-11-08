"""
Workflow Performance Analyzer
Tracks timing and memory usage of each step in the avatar workflow
"""

import time
import psutil
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class StepMetrics:
    """Metrics for a single workflow step"""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_before: Optional[float] = None
    memory_after: Optional[float] = None
    memory_delta: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def complete(self, success: bool = True, error: Optional[str] = None, **metadata):
        """Mark step as complete and record metrics"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error = error
        self.metadata.update(metadata)

        # Memory after
        process = psutil.Process(os.getpid())
        self.memory_after = process.memory_info().rss / 1024 / 1024  # MB
        if self.memory_before:
            self.memory_delta = self.memory_after - self.memory_before

    def __str__(self):
        status = "✅" if self.success else "❌"
        duration_str = f"{self.duration:.2f}s" if self.duration else "Running..."
        memory_str = f"+{self.memory_delta:.1f}MB" if self.memory_delta else ""
        return f"{status} {self.name}: {duration_str} {memory_str}"


class WorkflowAnalyzer:
    """
    Tracks workflow performance and identifies bottlenecks
    """

    def __init__(self):
        self.steps: List[StepMetrics] = []
        self.current_step: Optional[StepMetrics] = None
        self.workflow_start_time = time.time()
        self.process = psutil.Process(os.getpid())

    def start_step(self, name: str) -> StepMetrics:
        """Start tracking a new step"""
        # Complete previous step if not completed
        if self.current_step and self.current_step.end_time is None:
            self.current_step.complete(success=False, error="Incomplete - new step started")

        # Get current memory
        memory_mb = self.process.memory_info().rss / 1024 / 1024

        # Create new step
        step = StepMetrics(
            name=name,
            start_time=time.time(),
            memory_before=memory_mb
        )
        self.steps.append(step)
        self.current_step = step

        logger.info(f"▶️  Starting: {name} (Memory: {memory_mb:.1f}MB)")
        return step

    def complete_step(self, success: bool = True, error: Optional[str] = None, **metadata):
        """Complete the current step"""
        if self.current_step:
            self.current_step.complete(success=success, error=error, **metadata)
            logger.info(str(self.current_step))
            self.current_step = None

    def get_summary(self) -> Dict:
        """Get workflow performance summary"""
        total_duration = time.time() - self.workflow_start_time
        total_memory = self.process.memory_info().rss / 1024 / 1024

        completed_steps = [s for s in self.steps if s.duration is not None]
        failed_steps = [s for s in self.steps if not s.success]

        # Find slowest steps
        slowest_steps = sorted(completed_steps, key=lambda s: s.duration or 0, reverse=True)[:5]

        # Find memory hogs
        memory_hogs = sorted(
            [s for s in completed_steps if s.memory_delta],
            key=lambda s: s.memory_delta or 0,
            reverse=True
        )[:5]

        return {
            "total_duration": total_duration,
            "total_memory_mb": total_memory,
            "total_steps": len(self.steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "slowest_steps": [
                {
                    "name": s.name,
                    "duration": s.duration,
                    "memory_delta": s.memory_delta
                }
                for s in slowest_steps
            ],
            "memory_hogs": [
                {
                    "name": s.name,
                    "duration": s.duration,
                    "memory_delta": s.memory_delta
                }
                for s in memory_hogs
            ]
        }

    def print_report(self):
        """Print detailed performance report"""
        print("\n" + "="*80)
        print("🔍 WORKFLOW PERFORMANCE REPORT")
        print("="*80 + "\n")

        summary = self.get_summary()

        print(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
        print(f"💾 Total Memory: {summary['total_memory_mb']:.1f}MB")
        print(f"📊 Steps Completed: {summary['completed_steps']}/{summary['total_steps']}")
        if summary['failed_steps'] > 0:
            print(f"❌ Failed Steps: {summary['failed_steps']}")

        print("\n" + "-"*80)
        print("📈 ALL STEPS:")
        print("-"*80 + "\n")

        for i, step in enumerate(self.steps, 1):
            print(f"{i}. {step}")
            if step.metadata:
                for key, value in step.metadata.items():
                    print(f"   {key}: {value}")
            if step.error:
                print(f"   Error: {step.error}")

        if summary['slowest_steps']:
            print("\n" + "-"*80)
            print("🐌 SLOWEST STEPS:")
            print("-"*80 + "\n")
            for i, step in enumerate(summary['slowest_steps'], 1):
                print(f"{i}. {step['name']}: {step['duration']:.2f}s")

        if summary['memory_hogs']:
            print("\n" + "-"*80)
            print("💾 MEMORY INTENSIVE STEPS:")
            print("-"*80 + "\n")
            for i, step in enumerate(summary['memory_hogs'], 1):
                print(f"{i}. {step['name']}: +{step['memory_delta']:.1f}MB")

        print("\n" + "="*80 + "\n")


# Global workflow analyzer instance
workflow_analyzer = WorkflowAnalyzer()
