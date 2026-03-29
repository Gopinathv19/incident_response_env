"""Client for the simulated incident-response environment."""

from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient

from .models import (
    IncidentResponseAction,
    IncidentResponseObservation,
    IncidentResponseState,
)

if TYPE_CHECKING:
    from openenv.core.containers.runtime import ContainerProvider


class IncidentResponseEnv(
    EnvClient[
        IncidentResponseAction,
        IncidentResponseObservation,
        IncidentResponseState,
    ]
):
    """Typed client for interacting with the incident-response environment."""

    def _step_payload(self, action: IncidentResponseAction) -> Dict[str, Any]:
        """Convert an action model into a JSON-serializable request payload."""
        return action.model_dump(exclude_none=True)

    def _parse_result(
        self, payload: Dict[str, Any]
    ) -> StepResult[IncidentResponseObservation]:
        """Parse a server step/reset response into a typed StepResult."""
        observation = IncidentResponseObservation(**payload.get("observation", {}))
        reward = payload.get("reward", observation.reward)
        done = payload.get("done", observation.done)

        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
        )

    def _parse_state(self, payload: Dict[str, Any]) -> IncidentResponseState:
        """Parse the /state response into the typed incident state model."""
        return IncidentResponseState(**payload)
