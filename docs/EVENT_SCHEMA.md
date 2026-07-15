# Event schema

Every host change is a timezone-aware `ChangeEvent`. Required fields are `event_id`,
`event_type`, `source`, `project_id`, `object`, and `occurred_at`. Supported types are
`object.created`, `object.updated`, `object.deleted`, `relation.changed`, and `task.completed`.

```json
{"event_id":"evt-001","event_type":"object.updated","source":"host","project_id":"project","object":{"type":"chapter","id":"12","revision":"8"},"before":{"status":"draft"},"after":{"status":"published"},"occurred_at":"2026-07-15T10:30:00+08:00"}
```

Duplicate event IDs are stored once and never create a second report or Proposal.
