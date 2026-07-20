# Seeding Demo Records

The backend has a Faker-enabled seed command for creating realistic demo data.
By default it creates:

- 10 fixed demo articles
- 12 Faker users with profiles
- 60 Faker articles
- 60 Faker comments
- tags, article/tag links, notification settings, and ORM-seeded reaction activity

## Local or Deployed App Command

Run this after migrations:

```bash
python manage.py seed_articles
```

To choose a different article count:

```bash
python manage.py seed_articles --faker-count 75
```

The Faker records are deterministic. Re-running the command replaces records
whose article slug starts with `faker-demo-`, so it does not keep duplicating
the same seed articles.

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

The SQL file contains the Faker users/profiles, 60 Faker articles, 60 comments,
tags, article/tag links, and notification settings. Reaction activity is added
only by the Django management command because it uses Django's generic-relation
helpers.

## Seed Credentials

Faker accounts use:

- Email pattern: `faker1@authorshaven.app` through `faker12@authorshaven.app`
- Password: `Faker@12345`

Fixed demo accounts still use:

- Password: `Demo@12345`
