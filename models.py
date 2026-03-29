"""
Data models for the incident response environment.

This environment simulates a production outage investigation workflow. The
agent receives text-heavy observations such as alerts, logs, and metrics, then
uses diagnostic or remediation actions to resolve the incident.
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from openenv.core.env_server.types import Action, Observation, State
from pydantic import Field

IncidentActionName = Literal[
    "check_logs",
    "check_metrics",
    "check_db",
    "check_deploy_status",
    "check_dependencies",
    "restart_api",
    "restart_db",
    "rollback_deploy",
    "scale_service",
    "resolve_incident",
]

IncidentRootCause = Literal[
    "database_down",
    "bad_deploy",
    "memory_leak",
]

IncidentSeverity = Literal["low", "medium", "high", "critical"]
ServiceHealth = Literal["healthy", "degraded", "down"]
DependencyHealth = Literal["healthy", "degraded", "down", "unknown"]


class IncidentResponseAction(Action):
    """Action taken by the agent during diagnosis or remediation."""

    action: IncidentActionName
    target: Optional[str] = None


class IncidentResponseObservation(Observation):
    """Agent-visible observation for the current incident state."""

    summary: str = ""
    alerts: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    service_status: Dict[str, str] = Field(default_factory=dict)
    available_actions: List[IncidentActionName] = Field(default_factory=list)
    last_action_result: str = ""


class IncidentResponseState(State):
    """Internal simulation state for the incident-response environment."""

    root_cause: IncidentRootCause = "database_down"
    severity: IncidentSeverity = "medium"
    incident_resolved: bool = False
    diagnosis_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    max_steps: int = Field(default=12, ge=1)

    api_health: ServiceHealth = "degraded"
    db_health: DependencyHealth = "unknown"
    payment_gateway_health: DependencyHealth = "unknown"
    deployment_status: str = "unknown"

    latency_ms: float = Field(default=0.0, ge=0.0)
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    cpu_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    memory_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    disk_percent: float = Field(default=0.0, ge=0.0, le=100.0)

    alerts: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    action_history: List[str] = Field(default_factory=list)
    discovered_signals: List[str] = Field(default_factory=list)
