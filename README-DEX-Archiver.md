# DEX Trigger Archiver

This project implements a small Java CLI that:

- Connects to a SQL Server database (JDBC) and runs the supplied query to find clients to archive
- Calls the DEX trigger endpoint `/data-exchange/trigger?clientId={id}` for each client
- Stores the trigger response in S3 under `trigger/{clientid}/file/{clientid}_trigger_yyyymmdd.json` (or local filesystem for testing)

Configuration

Edit `src/main/resources/application.properties` or pass a properties file as the first CLI arg. Key settings:

- `db.url`, `db.user`, `db.password`
- `db.clients.query` - SQL to select clients (default provided in file)
- `dex.base.url` - base URL for DEX API
- `storage.mode` - `s3` or `local`
- `s3.bucket`, `s3.region` - for S3
- `local.output.dir` - when `storage.mode=local`

Run

Build and run (requires Gradle installed):

```bash
gradle build
gradle run --args='src/main/resources/application.properties'
```

Or run the jar produced in `build/libs`:

```bash
java -jar build/libs/dao-gradle-project-1.0.0.jar src/main/resources/application.properties
```

What exactly this project does is beyond the scope of this document.

Details / where to look

Orchestrator: ArchiverService.java
Calls fetcher.fetch(c.getClientId(), token) to get the response string, then calls:
uploader.upload(key, resp);
S3 implementation: S3Uploader.java
Uses the AWS SDK S3 client to putObject(bucket, key, RequestBody.fromString(content)).
Wiring: ArchiverApp.java
Chooses S3Uploader when storage.mode=s3 and constructs it with s3.region and s3.bucket from application.properties.


S3 key / file name format

The uploaded object key is constructed in ArchiverService as:
trigger/{clientId}/file/{clientId}_trigger_{yyyymmdd}.json

Example: for clientId = 123 on 2025‑11‑21 the object key will be:
trigger/123/file/123_trigger_20251121.json


What is uploaded

The content uploaded is the raw HTTP response body (a String) returned by {dex.base.url}/data-exchange/trigger?clientId=.... The code saves that string directly into S3 (as the object body).
If you want changes

Change filename/extension: edit the key format in ArchiverService.runArchive().
Upload a file from disk instead: modify ArchiverService to write the response to a temp file then call an uploader method that accepts a File/InputStream, and extend StorageUploader + S3Uploader accordingly.
Add metadata / content-type: update S3Uploader to set contentType("application/json") or add object metadata when building PutObjectRequest.
