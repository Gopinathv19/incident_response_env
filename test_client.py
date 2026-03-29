"""Simple smoke client for the incident-response environment.

Run this after starting the server:
    cd /home/gopi-nts0117/gopinath/openenv/OpenEnv
    python -m uvicorn envs.incident_response_env.server.app:app --host 127.0.0.1 --port 8000

Then in another terminal:
    cd /home/gopi-nts0117/gopinath/openenv/OpenEnv
    python envs/incident_response_env/test_client.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add the OpenEnv repo root so `envs.*` imports work when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from envs.incident_response_env import IncidentResponseAction, IncidentResponseEnv


def main() -> None:
    with IncidentResponseEnv(base_url="http://127.0.0.1:8000").sync() as env:
        result = env.reset()
        print("Reset summary:")
        print(result.observation.summary)
        print()

        # model_action = model(result)
        result = env.step(IncidentResponseAction(action="check_logs"))
        print("After check_logs:")
        for line in result.observation.logs:
            print(f"- {line}")
        print()

        result = env.step(IncidentResponseAction(action="check_metrics"))
        print("After check_metrics:")
        for key, value in result.observation.metrics.items():
            print(f"- {key}: {value}")
        print()

        print("Last action result:")
        print(result.observation.last_action_result)
        print()

        print("Reward / done:")
        print(result.reward, result.done)


if __name__ == "__main__":
    main()
