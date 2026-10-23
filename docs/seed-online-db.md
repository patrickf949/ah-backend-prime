# Seeding Demo Records

The backend has a seed command for creating realistic, natural-looking demo data.
By default it creates:

- 16 realistic authors with profiles (`amelia_stone`, `devon_pierce`, `lina_okafor`, `patrick2`, `vanessa_brown`, `melissa_parrish`, `william_pena`, `daniel_walsh`, `matthew_smith`, `jamie_shaw`, `daniel_collins`, `hunter_fisher`, `jennifer_stanley`, `barbara_miller`, `roger_terrell`, `edward_dorsey`)
- 11 fixed featured & custom articles (including `"The Best World Cup Song"` by `patrick2`)
- 60 realistic engineering, architecture, and product articles with natural slugs
- 60 realistic reader comments
- tags, article/tag links, notification settings, and ORM-seeded reaction activity
- automatically removes any legacy `faker_%` users or `faker-demo-%` articles

## Local or Hosted Database via `--db-url`

To seed your local database (using `.env`):

```bash
python manage.py seed_articles
```

To seed a hosted PostgreSQL database directly by passing its connection URL:

```bash
python manage.py seed_articles --db-url "postgresql://user:password@host:5432/dbname?sslmode=require"
```

To choose a different extra article count:

```bash
python manage.py seed_articles --faker-count 60 --db-url "postgresql://..."
```

## Generate SQL for an Online Database

Generate the SQL file without touching the configured database:

```bash
python manage.py seed_articles --sql-output docs/seed-online-db.sql --sql-only
```

Run the generated SQL against an online PostgreSQL database:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f docs/seed-online-db.sql
```

If your provider has a web SQL console, paste the contents of
`docs/seed-online-db.sql` and run it as one transaction.

## Seed Credentials

Seeded author accounts use:

- Password: `Demo@12345`

