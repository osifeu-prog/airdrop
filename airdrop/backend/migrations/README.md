Alembic lives under `migrations/`.

Local dev can bootstrap schema via `Base.metadata.create_all()` automatically,
but production should run Alembic migrations.

See `migrate.ps1`.
