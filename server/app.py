"""FastAPI application for the incident-response environment."""

from __future__ import annotations

# Support both in-repo and standalone imports
try:
    from openenv.core.env_server.http_server import create_app

    from ..models import IncidentResponseAction, IncidentResponseObservation
    from .incident_response_environment import IncidentResponseEnvironment
except ImportError:
    from openenv.core.env_server.http_server import create_app

    from incident_response_env.models import (
        IncidentResponseAction,
        IncidentResponseObservation,
    )
    from incident_response_env.server.incident_response_environment import (
        IncidentResponseEnvironment,
    )


app = create_app(
    IncidentResponseEnvironment,
    IncidentResponseAction,
    IncidentResponseObservation,
    env_name="incident_response_env",
)


def main() -> None:
    """Run the environment server directly with Uvicorn."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
