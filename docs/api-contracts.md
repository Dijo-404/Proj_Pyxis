# API Contracts

The versioned API is rooted at `/api/v1`. Contract schemas belong in
`backend/app/schemas/`; handlers should delegate business rules to services and
must not perform model inference or persistence directly.
