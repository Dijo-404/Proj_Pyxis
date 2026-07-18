# Data Flow

The canonical flow is:

```text
ingest -> normalize -> validate -> build financial twin -> score anomaly
       -> investigate -> compare scenarios -> human review -> report
```

Raw transactions and documents remain immutable. Derived features, AI output,
reviewer actions, and reports reference their source records through auditable IDs.
