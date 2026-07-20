"""Seed the database with demo articles for testing and demos.

Idempotent: fixed demo articles are matched by slug and updated. Faker
articles are recreated from deterministic input using the ``faker-demo-`` slug
prefix, so repeated runs do not keep adding duplicates.

    python manage.py seed_articles
    python manage.py seed_articles --faker-count 75
    python manage.py seed_articles --sql-output docs/seed-online-db.sql
    python manage.py seed_articles --sql-output docs/seed-online-db.sql --sql-only
"""
import random

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from authors.apps.authentication.models import User
from authors.apps.articles.models import Articles, Tag, Reaction, Comment


DEMO_TAG = 'demo'
FAKER_TAG = 'faker-demo'
FAKER_SLUG_PREFIX = 'faker-demo-'
DEMO_PASSWORD = 'Demo@12345'
FAKER_PASSWORD = 'Faker@12345'
DEFAULT_FAKER_COUNT = 60
DEFAULT_FAKER_AUTHORS = 12
DEFAULT_FAKER_SEED = 20260718

DEMO_AUTHORS = [
    {'username': 'amelia_stone', 'email': 'amelia.demo@authorshaven.app',
     'full_name': 'Amelia Stone', 'bio': 'Frontend engineer writing about the web.'},
    {'username': 'devon_pierce', 'email': 'devon.demo@authorshaven.app',
     'full_name': 'Devon Pierce', 'bio': 'Backend developer and coffee enthusiast.'},
    {'username': 'lina_okafor', 'email': 'lina.demo@authorshaven.app',
     'full_name': 'Lina Okafor', 'bio': 'Product designer who loves clean systems.'},
]

# (title, description, body, picsum_image_id, [tags])
DEMO_ARTICLES = [
    ("Getting Started with Django 6",
     "A practical tour of what's new and how to bootstrap a project.",
     "Django 6 sharpens the async story and trims boilerplate. In this walkthrough we scaffold a project, wire up the ORM, and ship a first endpoint. The goal is momentum: a running app you can extend, not a wall of configuration.",
     180, ['django', 'python', 'backend']),
    ("React 19 in Practice",
     "Hooks, transitions, and the patterns that actually hold up.",
     "React 19 leans hard into concurrent rendering. We look at where useTransition earns its keep, how to keep components honest, and the refactors that pay off as an app grows past its first few screens.",
     0, ['react', 'javascript', 'frontend']),
    ("Designing a REST API You Won't Hate",
     "Naming, pagination, and errors that make sense to clients.",
     "A good API is boring in the best way: predictable URLs, consistent errors, obvious pagination. We cover the small decisions that compound, and the ones you can defer without regret.",
     20, ['api', 'design', 'backend']),
    ("PostgreSQL Indexes Explained",
     "When an index helps, when it hurts, and how to tell.",
     "Indexes feel like magic until a query slows to a crawl. We build intuition for B-tree and partial indexes, read an EXPLAIN plan together, and learn to spot the write-amplification tax.",
     48, ['postgres', 'database', 'performance']),
    ("A Gentle Introduction to Docker",
     "Containers without the cargo-culting.",
     "Docker is easy to copy-paste and hard to understand. Here we start from why isolation matters, build a small image by hand, and demystify layers, caching, and the difference between an image and a container.",
     96, ['docker', 'devops']),
    ("Writing Tests That Earn Their Keep",
     "Coverage is a means, not the goal.",
     "The best test suite is the one that fails for the right reasons. We talk about testing behavior over implementation, the trap of brittle snapshots, and how to make a red build genuinely informative.",
     160, ['testing', 'quality']),
    ("Clean Git History for Teams",
     "Commits are documentation you write once and read forever.",
     "A tidy history is a gift to future readers, including yourself. We cover atomic commits, useful messages, and when to rebase versus merge without starting a holy war.",
     225, ['git', 'workflow']),
    ("Understanding JWT Authentication",
     "What the token holds, and what it must never hold.",
     "JWTs are simple to issue and easy to misuse. We decode one by hand, discuss signing versus encryption, and cover expiry, rotation, and the classic mistake of trusting a token's contents blindly.",
     201, ['auth', 'security', 'backend']),
    ("CSS Grid for Real Layouts",
     "From centering woes to full page structure.",
     "Grid finally made two-dimensional layout tractable. We rebuild a common blog layout from scratch, lean on named areas for readability, and keep it responsive without a single media-query hack.",
     119, ['css', 'frontend', 'design']),
    ("Deploying on a Budget",
     "Free tiers, cold starts, and how to demo without a credit card.",
     "You don't need a big bill to show real work. We map out free hosting for a Django API and a React frontend, talk through cold starts, and set expectations for a demo-grade deployment.",
     143, ['devops', 'deployment']),
]

FAKER_TAG_POOL = [
    'python', 'django', 'api', 'postgres', 'testing', 'security', 'frontend',
    'react', 'design', 'devops', 'deployment', 'javascript', 'product',
    'performance', 'architecture', 'career', 'automation', 'cloud',
]


class Command(BaseCommand):
    help = 'Seed the database with fixed demo articles plus Faker articles.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing fixed and Faker demo content before seeding.'
        )
        parser.add_argument(
            '--faker-count',
            type=int,
            default=DEFAULT_FAKER_COUNT,
            help='Number of Faker-generated articles to create. Default: 60.'
        )
        parser.add_argument(
            '--faker-authors',
            type=int,
            default=DEFAULT_FAKER_AUTHORS,
            help='Number of Faker-generated authors to create. Default: 12.'
        )
        parser.add_argument(
            '--faker-seed',
            type=int,
            default=DEFAULT_FAKER_SEED,
            help='Seed used to generate deterministic Faker records.'
        )
        parser.add_argument(
            '--sql-output',
            help='Write PostgreSQL seed SQL for the Faker records to this path.'
        )
        parser.add_argument(
            '--sql-only',
            action='store_true',
            help='Only write --sql-output; do not touch the configured DB.'
        )

    def handle(self, *args, **options):
        if options['faker_count'] < 51:
            raise SystemExit('--faker-count must be at least 51.')
        if options['faker_authors'] < 1:
            raise SystemExit('--faker-authors must be at least 1.')

        author_specs, article_specs = self._build_faker_specs(
            options['faker_count'],
            options['faker_authors'],
            options['faker_seed'],
        )

        if options['sql_output']:
            self._write_sql(options['sql_output'], author_specs, article_specs)

        if options['sql_only']:
            self.stdout.write(self.style.SUCCESS(
                'Wrote SQL only: {}'.format(options['sql_output'])
            ))
            return

        with transaction.atomic():
            if options['flush']:
                self._flush()
            else:
                self._flush_faker_articles()

            authors = self._ensure_authors()
            fake_authors = self._ensure_faker_authors(author_specs)
            fixed_articles = self._seed_fixed_articles(authors)
            fake_articles = self._seed_faker_articles(fake_authors, article_specs)
            self._seed_engagement(fixed_articles + fake_articles, authors + fake_authors)

        self.stdout.write(self.style.SUCCESS(
            'Seeded demo content: {} fixed articles, {} Faker articles, {} total authors.'.format(
                len(fixed_articles), len(fake_articles), len(authors) + len(fake_authors))
        ))

    def _seed_fixed_articles(self, authors):
        demo_tag, _ = Tag.objects.get_or_create(tag=DEMO_TAG)
        articles = []
        for index, (title, desc, body, img_id, tags) in enumerate(DEMO_ARTICLES):
            author = authors[index % len(authors)]
            slug = slugify(title) + '-demo'
            image = 'https://picsum.photos/id/{}/800/450'.format(img_id)

            article, _ = Articles.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'description': desc,
                    'body': body,
                    'image': image,
                    'author': author.profile,
                }
            )
            tag_objs = [demo_tag]
            for name in tags:
                tag_obj, _ = Tag.objects.get_or_create(tag=name)
                tag_objs.append(tag_obj)
            article.tagsList.set(tag_objs)
            articles.append(article)
        return articles

    def _seed_faker_articles(self, authors, article_specs):
        faker_tag, _ = Tag.objects.get_or_create(tag=FAKER_TAG)
        articles = []
        author_by_key = {user.email: user for user in authors}

        for spec in article_specs:
            author = author_by_key[spec['author_email']]
            article = Articles.objects.create(
                title=spec['title'],
                description=spec['description'],
                body=spec['body'],
                image=spec['image'],
                slug=spec['slug'],
                author=author.profile,
            )
            tag_objs = [faker_tag]
            for name in spec['tags']:
                tag_obj, _ = Tag.objects.get_or_create(tag=name)
                tag_objs.append(tag_obj)
            article.tagsList.set(tag_objs)

            Comment.objects.create(
                article=article,
                author=author.profile,
                body=spec['comment'],
                parentId=0,
            )
            articles.append(article)
        return articles

    def _ensure_authors(self):
        authors = []
        for spec in DEMO_AUTHORS:
            user = User.objects.filter(email=spec['email']).first()
            if user is None:
                user = User.objects.create_user(
                    username=spec['username'],
                    email=spec['email'],
                    password=DEMO_PASSWORD,
                )
                user.is_active = True
                user.save()
            profile = user.profile
            profile.full_name = spec['full_name']
            profile.bio = spec['bio']
            profile.save()
            authors.append(user)
        return authors

    def _ensure_faker_authors(self, author_specs):
        authors = []
        for spec in author_specs:
            user = User.objects.filter(email=spec['email']).first()
            if user is None:
                user = User.objects.create_user(
                    username=spec['username'],
                    email=spec['email'],
                    password=FAKER_PASSWORD,
                )
            user.is_active = True
            user.is_staff = False
            user.save()

            profile = user.profile
            profile.full_name = spec['full_name']
            profile.bio = spec['bio']
            profile.image = spec['image']
            profile.save()
            authors.append(user)
        return authors

    def _seed_engagement(self, articles, authors):
        """Give articles varied reactions so feeds are not all zeros."""
        emojis = [Reaction.LIKE, Reaction.LOVE, Reaction.FIRE,
                  Reaction.CLAP, Reaction.INSIGHTFUL, Reaction.WOW]
        rng = random.Random(42)

        for weight, article in enumerate(reversed(articles)):
            reactors = rng.sample(authors, k=rng.randint(0, min(len(authors), 6)))
            for user in reactors:
                emoji = emojis[(weight + user.pk) % len(emojis)]
                article.reactions.get_or_create(
                    user=user,
                    reaction=emoji,
                )

    def _build_faker_specs(self, article_count, author_count, seed):
        Faker.seed(seed)
        fake = Faker()
        rng = random.Random(seed)

        author_specs = []
        for index in range(author_count):
            first = fake.first_name()
            last = fake.last_name()
            username = 'faker_{}_{}'.format(index + 1, slugify(first + '-' + last))
            author_specs.append({
                'username': username[:255],
                'email': 'faker{}@authorshaven.app'.format(index + 1),
                'full_name': '{} {}'.format(first, last),
                'bio': fake.sentence(nb_words=12),
                'image': 'https://i.pravatar.cc/300?u=authors-haven-faker-{}'.format(index + 1),
            })

        article_specs = []
        for index in range(article_count):
            author = author_specs[index % len(author_specs)]
            topic = fake.bs().title()
            title = '{}: {}'.format(topic, fake.catch_phrase())[:200]
            slug = '{}{}'.format(FAKER_SLUG_PREFIX, index + 1)
            tags = sorted(rng.sample(FAKER_TAG_POOL, k=3))
            paragraphs = fake.paragraphs(nb=4)
            article_specs.append({
                'title': title,
                'description': fake.sentence(nb_words=12)[:200],
                'body': '\n\n'.join(paragraphs),
                'image': 'https://picsum.photos/seed/authors-haven-{}/800/450'.format(index + 1),
                'slug': slug,
                'author_email': author['email'],
                'tags': tags,
                'comment': fake.sentence(nb_words=14),
            })
        return author_specs, article_specs

    def _write_sql(self, output_path, author_specs, article_specs):
        sql = self._build_sql(author_specs, article_specs)
        with open(output_path, 'w', encoding='utf-8') as handle:
            handle.write(sql)
        self.stdout.write('Wrote online DB seed SQL to {}'.format(output_path))

    def _build_sql(self, author_specs, article_specs):
        password_hash = make_password(FAKER_PASSWORD)
        lines = [
            '-- Generated by: python manage.py seed_articles --sql-output docs/seed-online-db.sql',
            '-- Safe to rerun: Faker articles/comments/tag links are replaced by slug prefix.',
            'BEGIN;',
            '',
            "-- Remove previous Faker article data.",
            'DELETE FROM articles_comment WHERE article_id IN (SELECT id FROM articles_articles WHERE slug LIKE {});'.format(
                self._sql_literal(FAKER_SLUG_PREFIX + '%')),
            'DELETE FROM "articles_articles_tagsList" WHERE articles_id IN (SELECT id FROM articles_articles WHERE slug LIKE {});'.format(
                self._sql_literal(FAKER_SLUG_PREFIX + '%')),
            'DELETE FROM articles_articles WHERE slug LIKE {};'.format(
                self._sql_literal(FAKER_SLUG_PREFIX + '%')),
            '',
        ]

        all_tags = sorted({FAKER_TAG} | {tag for article in article_specs for tag in article['tags']})
        for tag in all_tags:
            lines.append(
                'INSERT INTO articles_tag (tag, created_at) VALUES ({tag}, NOW()) '
                'ON CONFLICT (tag) DO NOTHING;'.format(tag=self._sql_literal(tag))
            )
        lines.append('')

        for spec in author_specs:
            lines.extend([
                'INSERT INTO authentication_user '
                '(username, email, is_active, is_staff, is_superuser, created_at, updated_at) '
                'VALUES ({username}, {email}, TRUE, FALSE, FALSE, NOW(), NOW()) '
                'ON CONFLICT (email) DO UPDATE SET '
                'username = EXCLUDED.username, is_active = TRUE, updated_at = NOW();'.format(
                    username=self._sql_literal(spec['username']),
                    email=self._sql_literal(spec['email']),
                ),
                'INSERT INTO user_passwords (user_id, password_hash, updated_at) '
                'SELECT id, {password_hash}, NOW() FROM authentication_user WHERE email = {email} '
                'ON CONFLICT (user_id) DO UPDATE SET password_hash = EXCLUDED.password_hash, updated_at = NOW();'.format(
                    password_hash=self._sql_literal(password_hash),
                    email=self._sql_literal(spec['email']),
                ),
                'INSERT INTO profiles_profile (user_id, bio, full_name, image) '
                'SELECT id, {bio}, {full_name}, {image} FROM authentication_user WHERE email = {email} '
                'ON CONFLICT (user_id) DO UPDATE SET '
                'bio = EXCLUDED.bio, full_name = EXCLUDED.full_name, image = EXCLUDED.image;'.format(
                    bio=self._sql_literal(spec['bio']),
                    full_name=self._sql_literal(spec['full_name']),
                    image=self._sql_literal(spec['image']),
                    email=self._sql_literal(spec['email']),
                ),
                'INSERT INTO notification_notificationsetting '
                '(user_id, email_notifications, in_app_notifications) '
                'SELECT p.id, TRUE, TRUE FROM profiles_profile p '
                'JOIN authentication_user u ON u.id = p.user_id '
                'WHERE u.email = {email} AND NOT EXISTS ('
                'SELECT 1 FROM notification_notificationsetting existing WHERE existing.user_id = p.id'
                ');'.format(email=self._sql_literal(spec['email'])),
                '',
            ])

        for spec in article_specs:
            lines.extend([
                'INSERT INTO articles_articles '
                '("title", "description", "body", "createdAt", "updatedAt", "slug", "image", "author_id") '
                'SELECT {title}, {description}, {body}, NOW(), NOW(), {slug}, {image}, p.id '
                'FROM profiles_profile p '
                'JOIN authentication_user u ON u.id = p.user_id '
                'WHERE u.email = {email};'.format(
                    title=self._sql_literal(spec['title']),
                    description=self._sql_literal(spec['description']),
                    body=self._sql_literal(spec['body']),
                    slug=self._sql_literal(spec['slug']),
                    image=self._sql_literal(spec['image']),
                    email=self._sql_literal(spec['author_email']),
                ),
            ])
            for tag in [FAKER_TAG] + spec['tags']:
                lines.append(
                    'INSERT INTO "articles_articles_tagsList" (articles_id, tag_id) '
                    'SELECT a.id, t.id FROM articles_articles a, articles_tag t '
                    'WHERE a.slug = {slug} AND t.tag = {tag};'.format(
                        slug=self._sql_literal(spec['slug']),
                        tag=self._sql_literal(tag),
                    )
                )
            lines.append(
                'INSERT INTO articles_comment '
                '("body", "parentId", "createdAt", "updatedAt", "author_id", "article_id", "commentHistory") '
                'SELECT {body}, 0, NOW(), NOW(), p.id, a.id, {history} '
                'FROM articles_articles a '
                'JOIN profiles_profile p ON p.id = a.author_id '
                'WHERE a.slug = {slug};'.format(
                    body=self._sql_literal(spec['comment']),
                    history=self._sql_literal(''),
                    slug=self._sql_literal(spec['slug']),
                )
            )
            lines.append('')

        lines.extend(['COMMIT;', ''])
        return '\n'.join(lines)

    def _sql_literal(self, value):
        if value is None:
            return 'NULL'
        return "'{}'".format(str(value).replace("'", "''"))

    def _flush_faker_articles(self):
        Articles.objects.filter(slug__startswith=FAKER_SLUG_PREFIX).delete()

    def _flush(self):
        emails = [a['email'] for a in DEMO_AUTHORS]
        Articles.objects.filter(author__user__email__in=emails).delete()
        Articles.objects.filter(slug__startswith=FAKER_SLUG_PREFIX).delete()
        User.objects.filter(email__in=emails).delete()
        User.objects.filter(email__startswith='faker', email__endswith='@authorshaven.app').delete()
        self.stdout.write('Flushed existing demo content.')
