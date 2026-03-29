# Incident Response Environment

A simulated web-service outage debugging environment for OpenEnv.

## Scenarios

- `database_down`
- `bad_deploy`
- `memory_leak`

## Actions

- `check_logs`
- `check_metrics`
- `check_db`
- `check_deploy_status`
- `check_dependencies`
- `restart_api`
- `restart_db`
- `rollback_deploy`
- `scale_service`
- `resolve_incident`

## Run Locally

From the repository root:

```bash
python -m uvicorn envs.incident_response_env.server.app:app --host 127.0.0.1 --port 8000
```

Or from the environment directory:

```bash
cd OpenEnv/envs/incident_response_env
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000
```

## Quick Usage

```python
from envs.incident_response_env import IncidentResponseAction, IncidentResponseEnv

with IncidentResponseEnv(base_url="http://127.0.0.1:8000").sync() as env:
    result = env.reset()
    print(result.observation.summary)

    result = env.step(IncidentResponseAction(action="check_logs"))
    print(result.observation.logs)
```



cd /home/gopi-nts0117/gopinath/openenv/OpenEnv
python -m uvicorn envs.incident_response_env.server.app:app --host 127.0.0.1 --port 8000


cd /home/gopi-nts0117/gopinath/openenv/OpenEnv
python envs/incident_response_env/test_client.py
