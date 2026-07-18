# Database migrations

Member 2's compliance tables are managed by Alembic. From the repository root:

```bash
alembic upgrade head
alembic downgrade base
```

`PYXIS_DATABASE_PATH` selects the local SQLite file. Production deployments should
disable `PYXIS_DATABASE_AUTO_CREATE`, place the file on durable encrypted storage,
and apply reviewed migrations before startup.
