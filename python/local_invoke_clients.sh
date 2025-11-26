#!/usr/bin/env bash
# Local helper to simulate scheduled Lambda invocation that runs client archiving
set -euo pipefail
PY=python/src
EVENT='{"action": "run_clients"}'

echo "Running local client archiver simulation"
PYTHONPATH=$PY python3 -c "import json,os,yaml; from pyarchiver.archiver_lambda_service import ArchiverLambdaService; os.environ.setdefault('BUCKET','/tmp/pyarchiver-local'); os.environ.setdefault('PREFIX','trigger'); cfg=yaml.safe_load(open('python/config.yaml')); svc=ArchiverLambdaService(cfg); print(json.dumps(svc.run_once(), indent=2))"

echo "done"
