# Pyxis Backend

The backend combines two isolated feature sets behind one FastAPI application:

- The compliance workflow persists cases, evidence, documents, reviews, and reports in SQLite.
- The recovered financial intelligence and risk engine evaluates transactions, builds financial
  twins, compares scenarios, and keeps its simulation state in memory.

The compliance API is served at `/api/v1`. The complete simulation API is served at
`/api/v1/risk-engine`; its original non-conflicting transaction and customer endpoints remain
available as deprecated compatibility routes.

Both implementations are local-first. The backend has no PostgreSQL driver, server, or runtime
dependency, and Gemma remains behind a provider interface so a local runtime can be connected
without changing the API flow.
