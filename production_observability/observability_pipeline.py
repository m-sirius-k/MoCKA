"""Phase 7: wires the full observability/control pipeline together.

Event Stream Collector -> Telemetry Aggregator -> Trace Builder
    -> System Health Monitor -> Drift Detector -> Control Policy Engine
    -> (feedback to Execution Router)
"""

from __future__ import annotations

from typing import Optional

from control_policy_engine import ControlPolicyEngine, FeedbackCallback
from drift_detector import DriftDetector
from event_stream_collector import EventStreamCollector
from production_dashboard_model import ProductionDashboardModel
from system_health_monitor import SystemHealthMonitor
from telemetry_aggregator import TelemetryAggregator
from telemetry_registry import TelemetryEvent
from trace_builder import TraceBuilder


class ObservabilityPipeline:
    def __init__(self, feedback: Optional[FeedbackCallback] = None) -> None:
        self.collector = EventStreamCollector()
        self.aggregator = TelemetryAggregator(self.collector)
        self.trace_builder = TraceBuilder(self.aggregator)
        self.health_monitor = SystemHealthMonitor(self.collector)
        self.drift_detector = DriftDetector(self.collector, self.health_monitor)
        self.control_engine = ControlPolicyEngine(
            self.collector, self.drift_detector, self.health_monitor, feedback=feedback
        )
        self.dashboard = ProductionDashboardModel(
            self.aggregator, self.health_monitor, self.drift_detector, self.control_engine
        )

    def emit(self, event: TelemetryEvent) -> None:
        self.collector.emit(event)

    def snapshot(self):
        return self.dashboard.snapshot()
