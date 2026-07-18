# API Contracts

The versioned API is rooted at `/api/v1`. Contract schemas belong in
`backend/app/schemas/`; handlers should delegate business rules to services and
must not perform model inference or persistence directly.

The implemented compliance/case-management contract, endpoints, error envelope,
workflow rules, and local runtime configuration are documented in
[Backend Member 2](member-2-backend.md).
