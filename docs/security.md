# Security

- Keep customer data and model inference within the local deployment boundary.
- Treat source financial records as immutable.
- Separate AI recommendations from reviewer-controlled decisions.
- Audit all review, evidence-verification, and report-generation actions.
- Never learn from unresolved or confirmed suspicious behavior.
- Mask sensitive fields in logs and client views.

## Member 2 implementation controls

- The case assistant accepts only `localhost` or explicit private/loopback IP endpoints.
- Local AI HTTP calls ignore proxy environment variables and refuse redirects.
- Gemma receives one compact case context rather than raw database or document dumps.
- Uploaded documents are size-limited, extension-allowlisted, and stored under generated names.
- Model output is rejected unless it matches the required strict JSON schema.
- Final case dispositions are available only through the human review workflow.
- Every case, evidence, document, assistant, review, and report action creates an audit event.

Authentication and role mapping are not part of the supplied Member 2 assignment. Sandbox
reviewer IDs are asserted request values; production deployment must replace them with an
authenticated principal and enforce role-based authorization before exposure to users.
