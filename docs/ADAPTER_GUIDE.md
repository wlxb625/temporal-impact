# Adapter guide

Implement `HostAdapter.get_object()` and `HostAdapter.list_relations()` through the host
application's service layer. Map only object references, revision, fingerprint, summary,
importance, and relations with `ShadowMapper`; never copy complete host documents.

`apply_proposal()` is optional and raises by default. Temporal Impact does not invoke it.
