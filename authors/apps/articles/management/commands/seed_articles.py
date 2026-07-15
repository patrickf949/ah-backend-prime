"""Seed the database with demo articles for testing and demos.

Idempotent: running it again updates the same demo articles (matched by
slug) instead of creating duplicates. Safe to run on a fresh deploy.

    python manage.py seed_articles          # create/refresh demo content
    python manage.py seed_articles --flush  # delete demo content first
"""
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from authors.apps.authentication.models import User
from authors.apps.articles.models import Articles, Tag, Reaction


DEMO_TAG = 'demo'

DEMO_AUTHORS = [
    {'username': 'amelia_stone', 'email': 'amelia.demo@authorshaven.app',
     'full_name': 'Amelia Stone', 'bio': 'Frontend engineer writing about the web.'},
    {'username': 'devon_pierce', 'email': 'devon.demo@authorshaven.app',
     'full_name': 'Devon Pierce', 'bio': 'Backend developer and coffee enthusiast.'},
    {'username': 'lina_okafor', 'email': 'lina.demo@authorshaven.app',
     'full_name': 'Lina Okafor', 'bio': 'Product designer who loves clean systems.'},
]

DEMO_PASSWORD = 'Demo@12345'

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


class Command(BaseCommand):
    help = 'Seed the database with demo articles (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing demo content before seeding.'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        authors = self._ensure_authors()
        demo_tag, _ = Tag.objects.get_or_create(tag=DEMO_TAG)

        created, updated = 0, 0
        articles = []
        for index, (title, desc, body, img_id, tags) in enumerate(DEMO_ARTICLES):
            author = authors[index % len(authors)]
            slug = slugify(title) + '-demo'
            image = 'https://picsum.photos/id/{}/800/450'.format(img_id)

            article, was_created = Articles.objects.update_or_create(
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

            created += was_created
            updated += (not was_created)
            articles.append(article)

        self._seed_engagement(articles, authors)

        self.stdout.write(self.style.SUCCESS(
            'Seeded demo content: {} created, {} updated, {} authors.'.format(
                created, updated, len(authors))
        ))

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

    def _seed_engagement(self, articles, authors):
        """Give articles varied reactions and comments so the trending and
        popular feeds are actually differentiated (not all zeros)."""
        from authors.apps.articles.models import Comment

        emojis = [Reaction.LIKE, Reaction.LOVE, Reaction.FIRE,
                  Reaction.CLAP, Reaction.INSIGHTFUL, Reaction.WOW]
        rng = random.Random(42)  # deterministic seed data

        for weight, article in enumerate(reversed(articles)):
            # earlier-listed articles get more engagement -> clear ranking
            reactors = rng.sample(authors, k=rng.randint(0, len(authors)))
            for user in reactors:
                emoji = emojis[(weight + user.pk) % len(emojis)]
                article.reactions.get_or_create(
                    user=user, reaction=emoji
                )
            for i in range((weight % 3)):
                commenter = authors[(weight + i) % len(authors)]
                Comment.objects.get_or_create(
                    article=article,
                    author=commenter.profile,
                    body='Great write-up on "{}"! ({})'.format(
                        article.title, i + 1),
                    defaults={'parentId': 0},
                )

    def _flush(self):
        emails = [a['email'] for a in DEMO_AUTHORS]
        deleted, _ = Articles.objects.filter(
            author__user__email__in=emails).delete()
        User.objects.filter(email__in=emails).delete()
        self.stdout.write('Flushed existing demo content.')
