"""Seed the database with realistic articles, authors, comments, and reactions.

Idempotent: seeded articles are matched by slug and updated or recreated cleanly,
and any legacy ``faker_`` users or ``faker-demo-`` articles are purged automatically.

    python manage.py seed_articles
    python manage.py seed_articles --db-url "postgresql://user:pass@host:5432/dbname"
    python manage.py seed_articles --faker-count 60
    python manage.py seed_articles --sql-output docs/seed-online-db.sql
    python manage.py seed_articles --sql-output docs/seed-online-db.sql --sql-only
"""
import random

import dj_database_url
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.utils.text import slugify
from faker import Faker

from authors.apps.authentication.models import User
from authors.apps.articles.models import Articles, Tag, Reaction, Comment


DEMO_TAG = 'demo'
COMMUNITY_TAG = 'community'
LEGACY_FAKER_TAG = 'faker-demo'
LEGACY_FAKER_SLUG_PREFIX = 'faker-demo-'
DEMO_PASSWORD = 'Demo@12345'
FAKER_PASSWORD = 'Faker@12345'
DEFAULT_FAKER_COUNT = 60
DEFAULT_FAKER_AUTHORS = 12
DEFAULT_FAKER_SEED = 20260718

DEMO_AUTHORS = [
    {'username': 'amelia_stone', 'email': 'amelia.demo@authorshaven.app',
     'full_name': 'Amelia Stone', 'bio': 'Frontend engineer writing about modern web architecture and design systems.'},
    {'username': 'devon_pierce', 'email': 'devon.demo@authorshaven.app',
     'full_name': 'Devon Pierce', 'bio': 'Backend systems developer, database tinkerer, and espresso enthusiast.'},
    {'username': 'lina_okafor', 'email': 'lina.demo@authorshaven.app',
     'full_name': 'Lina Okafor', 'bio': 'Product designer and engineering lead focused on clarity and developer experience.'},
    {'username': 'patrick2', 'email': 'patrick3@mailinator.com',
     'full_name': 'Patrick Fitz', 'bio': 'Full-stack engineer, music fan, and creator of community stories.'},
]

REALISTIC_AUTHOR_PROFILES = [
    ('vanessa_brown', 'vanessa.brown@authorshaven.app', 'Vanessa Brown',
     'Staff infrastructure engineer specializing in cloud-native Python and distributed storage.'),
    ('melissa_parrish', 'melissa.parrish@authorshaven.app', 'Melissa Parrish',
     'Principal frontend architect exploring reactive UI patterns, accessibility, and web performance.'),
    ('william_pena', 'william.pena@authorshaven.app', 'William Pena',
     'Database reliability engineer writing about PostgreSQL internals, indexing, and query tuning.'),
    ('daniel_walsh', 'daniel.walsh@authorshaven.app', 'Daniel Walsh',
     'Security researcher and backend developer focused on authentication protocols and API hardening.'),
    ('matthew_smith', 'matthew.smith@authorshaven.app', 'Matthew Smith',
     'Platform engineer building resilient CI/CD pipelines and lightweight container workflows.'),
    ('jamie_shaw', 'jamie.shaw@authorshaven.app', 'Jamie Shaw',
     'Product-minded full-stack developer passionate about clean abstractions and pragmatic testing.'),
    ('daniel_collins', 'daniel.collins@authorshaven.app', 'Daniel Collins',
     'Lead software architect sharing lessons from scaling high-traffic web applications.'),
    ('hunter_fisher', 'hunter.fisher@authorshaven.app', 'Hunter Fisher',
     'Open-source maintainer and Python enthusiast writing deep dives into modern web frameworks.'),
    ('jennifer_stanley', 'jennifer.stanley@authorshaven.app', 'Jennifer Stanley',
     'Design systems engineer bridging the gap between Figma tokens and production CSS.'),
    ('barbara_miller', 'barbara.miller@authorshaven.app', 'Barbara Miller',
     'Engineering manager writing about team velocity, code review culture, and technical strategy.'),
    ('roger_terrell', 'roger.terrell@authorshaven.app', 'Roger Terrell',
     'Backend specialist focused on event-driven architecture, background jobs, and observability.'),
    ('edward_dorsey', 'edward.dorsey@authorshaven.app', 'Edward Dorsey',
     'Cloud architect helping startups ship reliable systems on lean infrastructure budgets.'),
]

# (title, description, body, image_url_or_picsum_id, [tags], optional_slug, optional_author_username)
DEMO_ARTICLES = [
    ("The Best World Cup Song",
     "FIFA 2010 - Shakira",
     '[{"id":"1784783454449","type":"image","url":"https://pub-68fa64bf882d44c484d6d7c977e5d12b.r2.dev/images/5550580a2db2420d86c3dd845b79d952.jpg"},{"id":"1784738268820","type":"text","content":"<p><strong>Samina</strong>&nbsp;mina&nbsp;Eh&nbsp;Eh&nbsp;<strong>Waka</strong>&nbsp;Waka&nbsp;<strong>Eh</strong>&nbsp;Eh</p><p>An unforgettable anthem that brought fans across every continent together during the 2010 tournament in South Africa.</p>"}]',
     'https://pub-68fa64bf882d44c484d6d7c977e5d12b.r2.dev/images/5550580a2db2420d86c3dd845b79d952.jpg',
     ['waka waka', 'music', 'culture'],
     'the-best-world-cup-song-0x46',
     'patrick2'),
    ("Getting Started with Django 6",
     "A practical tour of what's new and how to bootstrap a project.",
     "Django 6 sharpens the async story, introduces the built-in tasks framework, and trims boilerplate. In this walkthrough we scaffold a project, wire up the ORM, and ship a first endpoint. The goal is momentum: a running app you can extend, not a wall of configuration.",
     180, ['django', 'python', 'backend'], None, 'amelia_stone'),
    ("React 19 in Practice",
     "Hooks, transitions, and the patterns that actually hold up.",
     "React 19 leans hard into concurrent rendering. We look at where useTransition earns its keep, how to keep components honest, and the refactors that pay off as an app grows past its first few screens.",
     0, ['react', 'javascript', 'frontend'], None, 'devon_pierce'),
    ("Designing a REST API You Won't Hate",
     "Naming, pagination, and errors that make sense to clients.",
     "A good API is boring in the best way: predictable URLs, consistent errors, obvious pagination. We cover the small decisions that compound, and the ones you can defer without regret.",
     20, ['api', 'design', 'backend'], None, 'lina_okafor'),
    ("PostgreSQL Indexes Explained",
     "When an index helps, when it hurts, and how to tell.",
     "Indexes feel like magic until a query slows to a crawl. We build intuition for B-tree and partial indexes, read an EXPLAIN plan together, and learn to spot the write-amplification tax.",
     48, ['postgres', 'database', 'performance'], None, 'amelia_stone'),
    ("A Gentle Introduction to Docker",
     "Containers without the cargo-culting.",
     "Docker is easy to copy-paste and hard to understand. Here we start from why isolation matters, build a small image by hand, and demystify layers, caching, and the difference between an image and a container.",
     96, ['docker', 'devops'], None, 'devon_pierce'),
    ("Writing Tests That Earn Their Keep",
     "Coverage is a means, not the goal.",
     "The best test suite is the one that fails for the right reasons. We talk about testing behavior over implementation, the trap of brittle snapshots, and how to make a red build genuinely informative.",
     160, ['testing', 'quality'], None, 'lina_okafor'),
    ("Clean Git History for Teams",
     "Commits are documentation you write once and read forever.",
     "A tidy history is a gift to future readers, including yourself. We cover atomic commits, useful messages, and when to rebase versus merge without starting a holy war.",
     225, ['git', 'workflow'], None, 'amelia_stone'),
    ("Understanding JWT Authentication",
     "What the token holds, and what it must never hold.",
     "JWTs are simple to issue and easy to misuse. We decode one by hand, discuss signing versus encryption, and cover expiry, rotation, and the classic mistake of trusting a token's contents blindly.",
     201, ['auth', 'security', 'backend'], None, 'devon_pierce'),
    ("CSS Grid for Real Layouts",
     "From centering woes to full page structure.",
     "Grid finally made two-dimensional layout tractable. We rebuild a common blog layout from scratch, lean on named areas for readability, and keep it responsive without a single media-query hack.",
     119, ['css', 'frontend', 'design'], None, 'lina_okafor'),
    ("Deploying on a Budget",
     "Free tiers, cold starts, and how to demo without a credit card.",
     "You don't need a big bill to show real work. We map out free hosting for a Django API and a React frontend, talk through cold starts, and set expectations for a demo-grade deployment.",
     143, ['devops', 'deployment'], None, 'amelia_stone'),
]

ARTICLE_TITLE_TEMPLATES = [
    ("Scaling PostgreSQL Read Workloads Without Application Downtime",
     "Practical connection pooling, indexing, and query patterns for growing teams.",
     ['postgres', 'performance', 'architecture']),
    ("Modern State Management in React Without Boilerplate Fatigue",
     "How to separate server cache, URL state, and local UI state cleanly.",
     ['react', 'frontend', 'javascript']),
    ("Zero-Downtime Database Migrations in Continuous Delivery",
     "The expand-and-contract pattern for evolving schemas safely in production.",
     ['postgres', 'deployment', 'devops']),
    ("Building Resilient Background Jobs with Django 6 Tasks",
     "Moving slow I/O off the request path without complex broker infrastructure.",
     ['django', 'python', 'architecture']),
    ("Designing Accessible Component Libraries That Developers Enjoy Using",
     "Keyboard navigation, focus traps, and semantic markup that scale across teams.",
     ['frontend', 'design', 'react']),
    ("API Rate Limiting and Abuse Prevention for Public Endpoints",
     "Token buckets, sliding windows, and graceful degradation under traffic spikes.",
     ['api', 'security', 'architecture']),
    ("Fast Feedback Loops: Optimizing CI Pipelines for Python and JavaScript",
     "Caching dependencies, parallelizing test suites, and shaving minutes off builds.",
     ['testing', 'automation', 'devops']),
    ("Direct-to-Cloud Object Uploads Using Presigned URLs",
     "Keeping large media payloads off your application servers with S3-compatible storage.",
     ['cloud', 'architecture', 'performance']),
    ("Observability on a Shoestring: Structured Logging that Answers Questions",
     "What to log, how to correlate request IDs, and how to debug production incidents fast.",
     ['devops', 'deployment', 'architecture']),
    ("Why Idempotency Keys Matter in Modern REST APIs",
     "Preventing duplicate mutations when mobile and browser clients retry requests.",
     ['api', 'python', 'security']),
    ("Taming CSS Specificity in Large Multi-Team Codebases",
     "Scoped tokens, predictable layout primitives, and avoiding stylesheet entropy.",
     ['design', 'frontend', 'javascript']),
    ("Pragmatic Contract Testing Between Django Backends and SPA Frontends",
     "Catching serializer drift before it reaches staging or production.",
     ['testing', 'django', 'react']),
    ("From Monolith to Modular Boundaries Without Microservice Overhead",
     "Structuring Django apps with clear domain interfaces and minimal coupling.",
     ['django', 'python', 'architecture']),
    ("Optimizing Largest Contentful Paint on Media-Heavy Publishing Platforms",
     "Responsive images, lazy loading, and font delivery strategies that move the needle.",
     ['performance', 'frontend', 'design']),
    ("Secure Password Reset and Account Recovery Flows",
     "Time-bound tokens, single-use links, and preventing account enumeration.",
     ['security', 'api', 'python']),
    ("Effective Code Reviews for Distributed Engineering Teams",
     "How to write small pull requests and give feedback that elevates the whole team.",
     ['career', 'product', 'automation']),
    ("Understanding Connection Lifecycles in Gunicorn and WSGI",
     "Tuning workers, threads, and keep-alive timeouts for cloud container platforms.",
     ['python', 'deployment', 'performance']),
    ("Building Rich Block Editors in React Without Losing Your Mind",
     "Serialization, autosave drafts, and media management for modern publishing tools.",
     ['react', 'javascript', 'product']),
    ("PostgreSQL Full-Text Search vs Dedicated Search Engines",
     "How far native tsvector indexes and trigram matching can take your product.",
     ['postgres', 'performance', 'django']),
    ("Defensive Frontend Architecture: Handling Slow Networks Gracefully",
     "Loading states, optimistic updates, and clear user feedback when APIs wake up.",
     ['frontend', 'react', 'design']),
]

ARTICLE_PERSPECTIVES = [
    ("In Production", "Lessons learned from real traffic and operational trade-offs."),
    ("A Field Guide", "Step-by-step patterns you can apply to your stack today."),
    ("Deep Dive", "Under-the-hood mechanics and benchmarks that clarify the fundamentals."),
]

PARAGRAPH_POOL = [
    "When teams first ship a feature, the happy path usually gets all the attention. Over time, however, the edge cases—network timeouts, concurrent updates, and cold starts—define how reliable the product actually feels to everyday users. Investing a few hours into clear boundaries early on saves weeks of firefighting later.",
    "The trick is resisting unnecessary complexity until the metrics demand it. A well-indexed relational table and a straightforward synchronous or thread-backed workflow will often outperform a distributed queue with five moving parts, especially when operational bandwidth is limited.",
    "We started by measuring where latency actually lived across the request lifecycle. More than eighty percent of the perceived slowness came from unbatched queries and redundant serialization rather than raw compute. Once we made the data access pattern explicit, response times dropped by an order of magnitude.",
    "Good developer experience and good user experience reinforce each other. When the codebase has predictable conventions, fast tests, and clear error messages, engineers spend less energy guessing how things work and more energy polishing the details that readers notice immediately.",
    "Every architectural choice carries a maintenance price tag. Before introducing a new service or dependency, ask whether the problem can be solved with the primitives already in your framework. Simplicity is the ultimate multiplier for small, focused teams.",
    "Testing this layer requires thinking about failure modes rather than implementation details. By stubbing external network boundaries at the edge and asserting on observable state transitions, our test suite stays fast, deterministic, and resilient to internal refactoring.",
]

REALISTIC_COMMENTS = [
    "Great breakdown of the trade-offs here—keeping the architecture simple has saved our team so much debugging time.",
    "The section on measuring real bottlenecks before reaching for extra infrastructure really resonated with me.",
    "Bookmarked this for our next sprint planning. We ran into this exact edge case last month.",
    "Clear, practical, and right to the point. Would love a follow-up piece on how you monitor this in production.",
    "We switched to this pattern recently and our deployment pipeline has been noticeably more reliable.",
    "Appreciate the focus on pragmatic defaults rather than over-engineering from day one.",
    "This explained the underlying mechanics better than the official docs—thank you for sharing!",
    "The point about fast, deterministic tests is spot on. It completely changed how our team reviews PRs.",
]

FAKER_TAG_POOL = [
    'python', 'django', 'api', 'postgres', 'testing', 'security', 'frontend',
    'react', 'design', 'devops', 'deployment', 'javascript', 'product',
    'performance', 'architecture', 'career', 'automation', 'cloud',
]


class Command(BaseCommand):
    help = 'Seed the database with realistic articles, authors, comments, and reactions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--db-url',
            help='Optional PostgreSQL DATABASE_URL to connect to and seed directly.'
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing seeded and legacy faker content before seeding.'
        )
        parser.add_argument(
            '--faker-count',
            type=int,
            default=DEFAULT_FAKER_COUNT,
            help='Number of community articles to seed. Default: 60.'
        )
        parser.add_argument(
            '--faker-authors',
            type=int,
            default=DEFAULT_FAKER_AUTHORS,
            help='Number of community authors to seed. Default: 12.'
        )
        parser.add_argument(
            '--faker-seed',
            type=int,
            default=DEFAULT_FAKER_SEED,
            help='Seed used to generate deterministic records.'
        )
        parser.add_argument(
            '--sql-output',
            help='Write PostgreSQL seed SQL for the records to this path.'
        )
        parser.add_argument(
            '--sql-only',
            action='store_true',
            help='Only write --sql-output; do not touch the configured DB.'
        )

    def _configure_db_url(self, db_url):
        connections['default'].close()
        parsed = dj_database_url.parse(db_url, conn_max_age=600)
        parsed.setdefault('ATOMIC_REQUESTS', False)
        parsed.setdefault('AUTOCOMMIT', True)
        parsed.setdefault('TIME_ZONE', None)
        parsed.setdefault('CONN_HEALTH_CHECKS', False)
        parsed.setdefault('OPTIONS', {})
        parsed.setdefault('TEST', {})
        connections.databases['default'] = parsed
        connections['default'].settings_dict = parsed

    def handle(self, *args, **options):
        if options['faker_count'] < 51:
            raise SystemExit('--faker-count must be at least 51.')
        if options['faker_authors'] < 1:
            raise SystemExit('--faker-authors must be at least 1.')

        if options.get('db_url'):
            self._configure_db_url(options['db_url'])
            self.stdout.write(self.style.NOTICE('Configured target database from --db-url.'))

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
                self._flush(author_specs)
            else:
                self._flush_faker_articles(article_specs)

            authors = self._ensure_authors()
            fake_authors = self._ensure_faker_authors(author_specs)
            fixed_articles = self._seed_fixed_articles(authors)
            fake_articles = self._seed_faker_articles(fake_authors, article_specs)
            self._seed_engagement(fixed_articles + fake_articles, authors + fake_authors)

        self.stdout.write(self.style.SUCCESS(
            'Seeded content: {} featured articles, {} community articles, {} total authors.'.format(
                len(fixed_articles), len(fake_articles), len(authors) + len(fake_authors))
        ))

    def _seed_fixed_articles(self, authors):
        demo_tag, _ = Tag.objects.get_or_create(tag=DEMO_TAG)
        author_by_username = {u.username: u for u in authors}
        articles = []
        for index, item in enumerate(DEMO_ARTICLES):
            title, desc, body, img_ref, tags, custom_slug, author_username = item
            author = author_by_username.get(author_username) or authors[index % len(authors)]
            slug = custom_slug or (slugify(title) + '-demo')
            if isinstance(img_ref, int):
                image = 'https://picsum.photos/id/{}/800/450'.format(img_ref)
            else:
                image = img_ref

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
        community_tag, _ = Tag.objects.get_or_create(tag=COMMUNITY_TAG)
        articles = []
        author_by_key = {user.email: user for user in authors}

        for idx, spec in enumerate(article_specs):
            author = author_by_key[spec['author_email']]
            commenter = authors[(idx + 3) % len(authors)]
            article, _ = Articles.objects.update_or_create(
                slug=spec['slug'],
                defaults={
                    'title': spec['title'],
                    'description': spec['description'],
                    'body': spec['body'],
                    'image': spec['image'],
                    'author': author.profile,
                }
            )
            tag_objs = [community_tag]
            for name in spec['tags']:
                tag_obj, _ = Tag.objects.get_or_create(tag=name)
                tag_objs.append(tag_obj)
            article.tagsList.set(tag_objs)

            Comment.objects.filter(article=article).delete()
            Comment.objects.create(
                article=article,
                author=commenter.profile,
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
                user = User.objects.filter(username=spec['username']).first()
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
                user = User.objects.filter(username=spec['username']).first()
            if user is None:
                user = User.objects.create_user(
                    username=spec['username'],
                    email=spec['email'],
                    password=FAKER_PASSWORD,
                )
            else:
                user.username = spec['username']
                user.email = spec['email']
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
            reactors = rng.sample(authors, k=rng.randint(1, min(len(authors), 6)))
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
            if index < len(REALISTIC_AUTHOR_PROFILES):
                username, email, full_name, bio = REALISTIC_AUTHOR_PROFILES[index]
            else:
                first = fake.first_name()
                last = fake.last_name()
                slug_name = slugify(f"{first}-{last}").replace('-', '_')
                username = f"{slug_name}_{index + 1}"[:255]
                email = f"{slug_name}.{index + 1}@authorshaven.app"
                full_name = f"{first} {last}"
                bio = "Software engineer and technical writer sharing lessons from building web products."
            author_specs.append({
                'username': username,
                'email': email,
                'full_name': full_name,
                'bio': bio,
                'image': 'https://i.pravatar.cc/300?u={}'.format(username),
            })

        article_specs = []
        for index in range(article_count):
            author = author_specs[index % len(author_specs)]
            base_title, base_desc, base_tags = ARTICLE_TITLE_TEMPLATES[index % len(ARTICLE_TITLE_TEMPLATES)]
            perspective_Index = (index // len(ARTICLE_TITLE_TEMPLATES)) % len(ARTICLE_PERSPECTIVES)
            suffix_label, suffix_desc = ARTICLE_PERSPECTIVES[perspective_Index]

            if index < len(ARTICLE_TITLE_TEMPLATES):
                title = base_title
                description = base_desc
            else:
                title = f"{base_title}: {suffix_label}"
                description = f"{base_desc} {suffix_desc}"

            if index >= len(ARTICLE_TITLE_TEMPLATES) * len(ARTICLE_PERSPECTIVES):
                part_num = (index // (len(ARTICLE_TITLE_TEMPLATES) * len(ARTICLE_PERSPECTIVES))) + 2
                title = f"{title} (Part {part_num})"

            slug = slugify(title)[:240]
            extra_tag = rng.choice([t for t in FAKER_TAG_POOL if t not in base_tags])
            tags = sorted(set(base_tags[:2] + [extra_tag]))

            selected_paragraphs = [
                PARAGRAPH_POOL[(index + offset) % len(PARAGRAPH_POOL)]
                for offset in range(4)
            ]
            comment = REALISTIC_COMMENTS[index % len(REALISTIC_COMMENTS)]

            article_specs.append({
                'title': title[:200],
                'description': description[:200],
                'body': '\n\n'.join(selected_paragraphs),
                'image': 'https://picsum.photos/seed/{}/800/450'.format(slug),
                'slug': slug,
                'author_email': author['email'],
                'tags': tags,
                'comment': comment,
            })
        return author_specs, article_specs

    def _write_sql(self, output_path, author_specs, article_specs):
        sql = self._build_sql(author_specs, article_specs)
        with open(output_path, 'w', encoding='utf-8') as handle:
            handle.write(sql)
        self.stdout.write('Wrote online DB seed SQL to {}'.format(output_path))

    def _build_sql(self, author_specs, article_specs):
        password_hash = make_password(FAKER_PASSWORD)
        demo_password_hash = make_password(DEMO_PASSWORD)
        seeded_slugs = [s['slug'] for s in article_specs]
        slug_list_sql = ', '.join(self._sql_literal(s) for s in seeded_slugs)

        lines = [
            '-- Generated by: python manage.py seed_articles --sql-output docs/seed-online-db.sql',
            '-- Safe to rerun: removes legacy faker_ records and upserts realistic authors, articles, and comments.',
            'BEGIN;',
            '',
            '-- Remove legacy faker_ and previously seeded community article data.',
            'DELETE FROM articles_comment WHERE article_id IN (SELECT id FROM articles_articles WHERE slug LIKE {} OR slug IN ({}));'.format(
                self._sql_literal(LEGACY_FAKER_SLUG_PREFIX + '%'), slug_list_sql),
            'DELETE FROM "articles_articles_tagsList" WHERE articles_id IN (SELECT id FROM articles_articles WHERE slug LIKE {} OR slug IN ({}));'.format(
                self._sql_literal(LEGACY_FAKER_SLUG_PREFIX + '%'), slug_list_sql),
            'DELETE FROM articles_articles WHERE slug LIKE {} OR slug IN ({});'.format(
                self._sql_literal(LEGACY_FAKER_SLUG_PREFIX + '%'), slug_list_sql),
            "DELETE FROM notification_notificationsetting WHERE user_id IN (SELECT p.id FROM profiles_profile p JOIN authentication_user u ON u.id = p.user_id WHERE u.username LIKE 'faker_%');",
            "DELETE FROM profiles_profile WHERE user_id IN (SELECT id FROM authentication_user WHERE username LIKE 'faker_%');",
            "DELETE FROM user_passwords WHERE user_id IN (SELECT id FROM authentication_user WHERE username LIKE 'faker_%');",
            "DELETE FROM authentication_user WHERE username LIKE 'faker_%';",
            "DELETE FROM articles_tag WHERE tag = 'faker-demo';",
            '',
        ]

        fixed_tags = {t for item in DEMO_ARTICLES for t in item[4]}
        all_tags = sorted({DEMO_TAG, COMMUNITY_TAG} | fixed_tags | {tag for article in article_specs for tag in article['tags']})
        for tag in all_tags:
            lines.append(
                'INSERT INTO articles_tag (tag, created_at) VALUES ({tag}, NOW()) '
                'ON CONFLICT (tag) DO NOTHING;'.format(tag=self._sql_literal(tag))
            )
        lines.append('')

        all_authors = [
            {
                'username': a['username'],
                'email': a['email'],
                'full_name': a['full_name'],
                'bio': a['bio'],
                'image': 'https://i.pravatar.cc/300?u={}'.format(a['username']),
                'password_hash': demo_password_hash,
            }
            for a in DEMO_AUTHORS
        ] + [
            {
                **spec,
                'password_hash': password_hash,
            }
            for spec in author_specs
        ]

        for spec in all_authors:
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
                    password_hash=self._sql_literal(spec['password_hash']),
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
            for tag in [COMMUNITY_TAG] + spec['tags']:
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

    def _flush_faker_articles(self, article_specs=None):
        Articles.objects.filter(slug__startswith=LEGACY_FAKER_SLUG_PREFIX).delete()
        if article_specs:
            slugs = [s['slug'] for s in article_specs]
            Articles.objects.filter(slug__in=slugs).delete()
        User.objects.filter(username__startswith='faker_').delete()
        Tag.objects.filter(tag=LEGACY_FAKER_TAG).delete()

    def _flush(self, author_specs=None):
        emails = [a['email'] for a in DEMO_AUTHORS]
        if author_specs:
            emails.extend([a['email'] for a in author_specs])
        Articles.objects.filter(author__user__email__in=emails).delete()
        Articles.objects.filter(slug__startswith=LEGACY_FAKER_SLUG_PREFIX).delete()
        User.objects.filter(email__in=emails).delete()
        User.objects.filter(username__startswith='faker_').delete()
        User.objects.filter(email__startswith='faker', email__endswith='@authorshaven.app').delete()
        Tag.objects.filter(tag=LEGACY_FAKER_TAG).delete()
        self.stdout.write('Flushed existing seeded content.')
