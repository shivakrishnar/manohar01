# Python port of dex-trigger-response-archive

This folder contains a lightweight Python port of the Java application present on the `main` branch.

Quick start

1. Create and activate a virtualenv (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Provide configuration (example `config.yaml` is included).

3. Run the small CLI tool:

```bash
python -m pyarchiver.archiver_app config.yaml
```

Notes

- This port mirrors the Java structure (simplified) with: ArchiverApp (CLI), ArchiverService, TriggerFetcher, TokenProvider, DAOs, and storage uploaders.
- The S3 uploader uses `boto3`.
- The Python implementation is intentionally minimal — a drop-in skeleton to make migration and testing easier.

Packaging
---------

The repository includes a ``pyproject.toml`` in `python/` so you can build standard Python artifacts (wheel + sdist).

Local build example (recommended in a venv):

```bash
python3 -m pip install --upgrade build
cd python
./build.sh
```

Artifacts will be written to `python/dist/`.

Lambda deployment and scheduled runs
-----------------------------------

This package includes a Serverless Application Model (SAM) template at `python/template.yaml` that creates a Lambda function which runs daily (you can change the schedule) and archives trigger responses to S3.

Environment variables and parameters used by the Lambda function
- BUCKET (required) — target S3 bucket name
- PREFIX (optional) — S3 key prefix (default: trigger)
- CLIENTS_API_URL (optional) — when set, the Lambda will fetch the list of clients from this URL (returns JSON)
- TRIGGER_BASE_URL (optional) — used to build trigger URL when client does not specify one
- CLIENT_TOKEN_URL (optional) — OAuth token URL for client credentials flow

Deploy via SAM (example):

```bash
cd python
# package (creates artifacts/ prepared code)
sam build
# deploy interactively and pass the archive bucket name
sam deploy --guided
```

Local simulation
----------------
You can simulate a scheduled run locally without deploying by running:

```bash
chmod +x local_invoke_clients.sh
./local_invoke_clients.sh
```

Provide real `CLIENTS_API_URL` and token endpoints via environment variables when running in Lambda.

Ticket / functional requirements (DEX-API-Archive Trigger File Response)
-------------------------------------------------------------------

Summary of requirement implemented by this package:

- Find clients that have the dex-api scope `dex/trigger:all` (the ticket SQL can be used to generate the list in an API)
- For each such client call the trigger endpoint `/data-exchange/trigger` (per-client `trigger_url` or a base `TRIGGER_BASE_URL` is supported)
- Save the raw JSON response and archive it to S3 using the structure:
	- bucket/<prefix>/trigger/<clientid>/<clientid>_trigger_YYYYMMDD.json

The `python/config.yaml` contains an example `clients` list useful for local testing if you don't have a real clients API available.

SQL (example) to produce the client list for the CLIENTS_API_URL:

```sql
use Mediant;
SELECT DISTINCT c.ClientID AS client_id, c.name, c.OAuth2ClientCredentialsID AS oauth_client_id
FROM Client c
INNER JOIN ClientServiceExt cs ON c.ClientID = cs.ClientID
WHERE c.OAuth2ClientCredentialsID is not NULL
AND cs.ServiceID IN (2,8,3,4,5);
```

The Lambda will look for credentials for each client (oauth_client_id / oauth_client_secret) and attempt client-credentials token exchange using `CLIENT_TOKEN_URL` (or a per-client token_url).
