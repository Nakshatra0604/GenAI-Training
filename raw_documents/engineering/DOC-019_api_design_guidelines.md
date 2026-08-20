# API Design Guidelines

## Resource Naming

APIs at NexaCore Solutions use plural nouns for resource collections, for
example `/orders` rather than `/order` or `/getOrders`. Nested resources
should reflect a genuine ownership relationship, such as
`/orders/{id}/line-items`, rather than being nested purely for
convenience.

## Versioning

Breaking changes require a new API version, expressed as a path prefix
such as `/v2/orders`. Non-breaking additions, such as a new optional field,
do not require a new version. Deprecated versions are supported for a
minimum of twelve months after a replacement version is available.

## Request and Response Format

All APIs accept and return JSON by default. Field names use camelCase, and
timestamps are represented in ISO 8601 format with an explicit timezone.
Pagination uses a cursor-based approach rather than page numbers for any
collection that could grow large.

## Error Responses

Error responses include a machine-readable error code, a human-readable
message, and, where relevant, the specific field that caused a validation
error. Error codes are documented and stable; the wording of the
human-readable message may change without being considered a breaking
change.

## Authentication

Internal service-to-service APIs authenticate using short-lived tokens
issued by the internal identity service. Public-facing APIs use API keys
scoped to the minimum permissions required, following the same
least-privilege principle described in the Access Control Policy.

## Documentation

Every API endpoint must have accompanying documentation generated from the
API specification, including example requests and responses. Undocumented
endpoints are not considered ready for other teams to depend on.
