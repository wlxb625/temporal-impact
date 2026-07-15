# Integration guide

Use the SDK for Python hosts or `temporal-impact serve` for other applications. Post the event
JSON to `POST /analyze`; retrieve the report by ID and list proposals. The sidecar is local,
read-only, and stores only shadow references and analysis metadata in SQLite.

Set `TEMPORAL_IMPACT_DB_URL` to change the SQLite location.
