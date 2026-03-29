"""Server-side simulation for the incident-response environment."""

from __future__ import annotations
import random
import uuid
from typing import Dict, List, Optional

from openenv.core.env_server.interfaces import Environment

from ..models import (
    IncidentResponseAction,
    IncidentResponseObservation,
    IncidentResponseState,
)

class IncidentResponseEnvironment(Environment):
    """Simulated web-service outage debugging environment."""

    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self, seed: int = 3407, max_steps: int = 12):
        super().__init__()
        self.rng = random.Random(seed)
        self.default_seed = seed
        self.default_max_steps = max_steps
        self._state: IncidentResponseState | None = None

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs,
    ) -> IncidentResponseObservation:
        if seed is not None:
            self.rng.seed(seed)

        root_cause = self.rng.choice(
            [
                "database_down",
                "bad_deploy",
                "memory_leak",
            ]
        )
        severity = self.rng.choice(["medium", "high", "critical"])

        scenario = self._build_scenario(root_cause=root_cause, severity=severity)

        self._state = IncidentResponseState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            max_steps=self.default_max_steps,
            root_cause=root_cause,
            severity=severity,
            incident_resolved=False,
            diagnosis_confidence=0.0,
            api_health=scenario["api_health"],
            db_health=scenario["db_health"],
            payment_gateway_health=scenario["payment_gateway_health"],
            deployment_status=scenario["deployment_status"],
            latency_ms=scenario["latency_ms"],
            error_rate=scenario["error_rate"],
            cpu_percent=scenario["cpu_percent"],
            memory_percent=scenario["memory_percent"],
            disk_percent=scenario["disk_percent"],
            alerts=list(scenario["alerts"]),
            logs=list(scenario["logs"]),
            action_history=[],
            discovered_signals=[],
        )
        return self._make_observation(last_action_result="Incident created.")

    def step(
        self,
        action: IncidentResponseAction,
        timeout_s: Optional[float] = None,
        **kwargs,
    ) -> IncidentResponseObservation:
        if self._state is None:
            raise RuntimeError("Environment must be reset before step().")

        state = self._state
        reward = -0.05
        done = False
        action_name = action.action
        state.action_history.append(action_name)
        state.step_count += 1

        if action_name == "check_logs":
            reward += self._handle_check_logs()
            last_action_result = "Fetched recent application logs."
        elif action_name == "check_metrics":
            reward += self._handle_check_metrics()
            last_action_result = "Fetched service metrics dashboard."
        elif action_name == "check_db":
            reward += self._handle_check_db()
            last_action_result = "Checked database health and connectivity."
        elif action_name == "check_deploy_status":
            reward += self._handle_check_deploy_status()
            last_action_result = "Checked the latest deployment status."
        elif action_name == "check_dependencies":
            reward += self._handle_check_dependencies()
            last_action_result = "Checked upstream dependency health."
        elif action_name == "restart_api":
            reward += self._handle_restart_api()
            last_action_result = "Restarted checkout-service API pods."
        elif action_name == "restart_db":
            reward += self._handle_restart_db()
            last_action_result = "Restarted the checkout database."
        elif action_name == "rollback_deploy":
            reward += self._handle_rollback_deploy()
            last_action_result = "Rolled back the latest deployment."
        elif action_name == "scale_service":
            reward += self._handle_scale_service()
            last_action_result = "Scaled the checkout-service horizontally."
        elif action_name == "resolve_incident":
            reward += self._handle_resolve_incident()
            last_action_result = "Marked incident as resolved."
            done = state.incident_resolved
        else:
            reward -= 0.2
            last_action_result = f"Unsupported action: {action_name}."

        if state.step_count >= state.max_steps and not state.incident_resolved:
            done = True
            reward -= 4.0
            last_action_result = (
                f"{last_action_result} Step limit reached before recovery."
            )

        observation = self._make_observation(last_action_result=last_action_result)
        observation.reward = reward
        observation.done = done
        return observation

    @property
    def state(self) -> IncidentResponseState:
        if self._state is None:
            raise RuntimeError("Environment state is unavailable before reset().")
        return self._state

    def _build_scenario(self, root_cause: str, severity: str) -> Dict[str, object]:
        base: Dict[str, object] = {
            "api_health": "degraded",
            "db_health": "unknown",
            "payment_gateway_health": "unknown",
            "deployment_status": "unknown",
            "latency_ms": 2800.0,
            "error_rate": 0.24,
            "cpu_percent": 72.0,
            "memory_percent": 68.0,
            "disk_percent": 61.0,
            "alerts": [
                "ALERT: checkout-service latency above SLO",
                "ALERT: checkout-service error rate elevated",
            ],
            "logs": [
                "WARN request timeout while processing checkout",
                "INFO retrying failed downstream call",
            ],
        }

        if root_cause == "database_down":
            base.update(
                {
                    "api_health": "down",
                    "db_health": "down",
                    "deployment_status": "stable",
                    "latency_ms": 4200.0,
                    "error_rate": 0.55,
                    "cpu_percent": 38.0,
                    "memory_percent": 47.0,
                    "alerts": [
                        "ALERT: checkout-service availability below threshold",
                        "ALERT: database connection failures detected",
                    ],
                    "logs": [
                        "ERROR failed to connect to postgres: connection refused",
                        "ERROR db pool exhausted after repeated retries",
                    ],
                }
            )
        elif root_cause == "bad_deploy":
            base.update(
                {
                    "api_health": "down",
                    "db_health": "healthy",
                    "payment_gateway_health": "healthy",
                    "deployment_status": "failed rollout",
                    "latency_ms": 3500.0,
                    "error_rate": 0.48,
                    "cpu_percent": 44.0,
                    "memory_percent": 59.0,
                    "alerts": [
                        "ALERT: elevated 5xx responses after recent deployment",
                        "ALERT: checkout-service pods restarting",
                    ],
                    "logs": [
                        "ERROR migration version mismatch in checkout-service startup",
                        "ERROR new release failed readiness probe on /health",
                    ],
                }
            )
        elif root_cause == "memory_leak":
            base.update(
                {
                    "api_health": "degraded",
                    "db_health": "healthy",
                    "payment_gateway_health": "healthy",
                    "deployment_status": "stable",
                    "latency_ms": 3100.0,
                    "error_rate": 0.19,
                    "cpu_percent": 86.0,
                    "memory_percent": 96.0,
                    "alerts": [
                        "ALERT: checkout-service memory usage critically high",
                        "ALERT: increased pod restarts on checkout-service",
                    ],
                    "logs": [
                        "WARN heap usage above 95 percent for 10m",
                        "ERROR process restarted after out-of-memory kill",
                    ],
                }
            )

        if severity == "critical":
            base["latency_ms"] = float(base["latency_ms"]) * 1.15
            base["error_rate"] = min(1.0, float(base["error_rate"]) + 0.08)
        elif severity == "medium":
            base["latency_ms"] = float(base["latency_ms"]) * 0.9
            base["error_rate"] = max(0.05, float(base["error_rate"]) - 0.03)

        return base

    def _make_observation(
        self, last_action_result: str = ""
    ) -> IncidentResponseObservation:
        state = self.state
        summary = (
            "Checkout-service incident in progress. "
            f"API is {state.api_health}, latency is {state.latency_ms:.0f} ms, "
            f"and error rate is {state.error_rate:.0%}."
        )

        return IncidentResponseObservation(
            summary=summary,
            alerts=list(state.alerts),
            logs=list(state.logs[-5:]),
            metrics={
                "latency_ms": round(state.latency_ms, 2),
                "error_rate": round(state.error_rate, 4),
                "cpu_percent": round(state.cpu_percent, 2),
                "memory_percent": round(state.memory_percent, 2),
                "disk_percent": round(state.disk_percent, 2),
            },
            service_status={
                "checkout_service": state.api_health,
                "database": state.db_health,
                "payment_gateway": state.payment_gateway_health,
                "deployment": state.deployment_status,
            },
            available_actions=[
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
            ],
            last_action_result=last_action_result,
            metadata={
                "step_count": state.step_count,
                "severity": state.severity,
            },
        )

    def _handle_check_logs(self) -> float:
        state = self.state
        self._record_signal(f"logs:{state.root_cause}")
        return 0.2

    def _handle_check_metrics(self) -> float:
        state = self.state
        self._record_signal("metrics")
        return 0.15 if state.root_cause == "memory_leak" else 0.1

    def _handle_check_db(self) -> float:
        state = self.state
        if state.root_cause == "database_down":
            state.db_health = "down"
            self._record_signal("db_down_confirmed")
            state.logs.append("ERROR database health check failed: database unavailable")
            return 0.3

        state.db_health = "healthy"
        state.logs.append("INFO database health check passed")
        self._record_signal("db_healthy")
        return -0.05

    def _handle_check_deploy_status(self) -> float:
        state = self.state
        if state.root_cause == "bad_deploy":
            state.deployment_status = "failed rollout"
            self._record_signal("deploy_failed")
            state.logs.append("INFO deployment dashboard shows unhealthy release candidate")
            return 0.3

        if state.deployment_status == "unknown":
            state.deployment_status = "stable"
        self._record_signal("deploy_checked")
        state.logs.append("INFO deployment status looks stable")
        return -0.05

    def _handle_check_dependencies(self) -> float:
        state = self.state
        if state.payment_gateway_health == "unknown":
            state.payment_gateway_health = "healthy"
        self._record_signal("dependencies_checked")
        state.logs.append("INFO upstream dependencies responding normally")
        return -0.05

    def _handle_restart_api(self) -> float:
        state = self.state
        if state.root_cause == "memory_leak":
            state.api_health = "healthy"
            state.latency_ms = 620.0
            state.error_rate = 0.03
            state.cpu_percent = 46.0
            state.memory_percent = 54.0
            state.incident_resolved = True
            state.logs.append("INFO checkout-service recovered after API restart")
            return 8.0

        if state.root_cause == "bad_deploy":
            state.logs.append("WARN restarted pods but new release still fails readiness checks")
            return -0.5

        state.logs.append("WARN API restart did not address the underlying issue")
        return -0.3

    def _handle_restart_db(self) -> float:
        state = self.state
        if state.root_cause == "database_down":
            state.db_health = "healthy"
            state.api_health = "healthy"
            state.latency_ms = 540.0
            state.error_rate = 0.02
            state.incident_resolved = True
            state.logs.append("INFO database restarted and connections restored")
            return 8.0

        state.logs.append("WARN database restart was unnecessary for this incident")
        return -0.4

    def _handle_rollback_deploy(self) -> float:
        state = self.state
        if state.root_cause == "bad_deploy":
            state.deployment_status = "rolled back"
            state.api_health = "healthy"
            state.latency_ms = 700.0
            state.error_rate = 0.02
            state.incident_resolved = True
            state.logs.append("INFO checkout-service recovered after rollback")
            return 8.0

        state.logs.append("WARN rollback completed but incident symptoms remain")
        return -0.4

    def _handle_scale_service(self) -> float:
        state = self.state
        if state.root_cause == "memory_leak":
            state.api_health = "degraded"
            state.latency_ms = max(1200.0, state.latency_ms - 900.0)
            state.error_rate = max(0.08, state.error_rate - 0.05)
            state.cpu_percent = max(55.0, state.cpu_percent - 20.0)
            state.memory_percent = max(78.0, state.memory_percent - 8.0)
            state.logs.append("INFO scaling reduced pressure but memory growth continues")
            return 0.25
        state.logs.append("WARN scaling had no meaningful effect on the incident")
        return -0.15

    def _handle_resolve_incident(self) -> float:
        state = self.state
        if state.incident_resolved:
            return 0.5
        return -2.0

    def _record_signal(self, signal: str) -> None:
        state = self.state
        if signal not in state.discovered_signals:
            state.discovered_signals.append(signal)
            state.diagnosis_confidence = min(
                1.0, state.diagnosis_confidence + 0.25
            )
