"""SEO helpers and views for articles.

Provides per-article SEO metadata (meta tags, Open Graph, Twitter cards,
schema.org JSON-LD) plus site-wide discovery endpoints: sitemap.xml,
robots.txt and an RSS feed.
"""
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.utils.html import strip_tags
from django.utils.text import Truncator

from .models import Articles

META_TITLE_LENGTH = 60
META_DESCRIPTION_LENGTH = 155


def article_url(article):
    """Canonical (frontend) URL of an article"""
    return '{}/article/{}'.format(settings.FRONTEND_URL.rstrip('/'),
                                  article.slug)


def build_seo_meta(article):
    """Build SEO metadata for an article suitable for meta/OG/Twitter tags"""
    description = strip_tags(article.description or article.body or '')
    description = Truncator(' '.join(description.split())).chars(
        META_DESCRIPTION_LENGTH, truncate='…')
    keywords = [tag.tag for tag in article.tagsList.all()]
    canonical = article_url(article)

    return {
        'meta_title': Truncator(article.title).chars(
            META_TITLE_LENGTH, truncate='…'),
        'meta_description': description,
        'keywords': keywords,
        'canonical_url': canonical,
        'og': {
            'og:type': 'article',
            'og:title': article.title,
            'og:description': description,
            'og:url': canonical,
            'og:image': article.image or '',
            'article:published_time': article.createdAt.isoformat(),
            'article:modified_time': article.updatedAt.isoformat(),
            'article:author': article.author.user.username,
            'article:tag': keywords,
        },
        'twitter': {
            'twitter:card': 'summary_large_image' if article.image
            else 'summary',
            'twitter:title': article.title,
            'twitter:description': description,
            'twitter:image': article.image or '',
        },
    }


def build_structured_data(article):
    """Build schema.org Article JSON-LD for search engine rich results"""
    meta = build_seo_meta(article)
    return {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': article.title,
        'description': meta['meta_description'],
        'image': [article.image] if article.image else [],
        'keywords': ', '.join(meta['keywords']),
        'wordCount': len((article.body or '').split()),
        'datePublished': article.createdAt.isoformat(),
        'dateModified': article.updatedAt.isoformat(),
        'author': {
            '@type': 'Person',
            'name': article.author.user.username,
        },
        'publisher': {
            '@type': 'Organization',
            'name': "Authors' Haven",
            'url': settings.FRONTEND_URL,
        },
        'mainEntityOfPage': {
            '@type': 'WebPage',
            '@id': meta['canonical_url'],
        },
    }


def sitemap_view(request):
    """Serve a sitemap.xml of all article canonical URLs"""
    articles = Articles.objects.order_by('-updatedAt')
    urls = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    urls.append(
        '<url><loc>{}</loc><changefreq>daily</changefreq>'
        '<priority>1.0</priority></url>'.format(
            settings.FRONTEND_URL.rstrip('/'))
    )
    for article in articles:
        urls.append(
            '<url><loc>{}</loc><lastmod>{}</lastmod>'
            '<changefreq>weekly</changefreq><priority>0.8</priority>'
            '</url>'.format(
                article_url(article),
                article.updatedAt.strftime('%Y-%m-%d'))
        )
    urls.append('</urlset>')
    return HttpResponse('\n'.join(urls), content_type='application/xml')


def robots_view(request):
    """Serve robots.txt pointing crawlers at the sitemap"""
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /api/',
        'Sitemap: {}/sitemap.xml'.format(
            request.build_absolute_uri('/').rstrip('/')),
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


class LatestArticlesFeed(Feed):
    """RSS feed of the most recent articles"""
    title = "Authors' Haven — Latest Articles"
    description = "The newest stories published on Authors' Haven"

    def link(self):
        return settings.FRONTEND_URL

    def items(self):
        return Articles.objects.order_by('-createdAt')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return build_seo_meta(item)['meta_description']

    def item_link(self, item):
        return article_url(item)

    def item_pubdate(self, item):
        return item.createdAt

    def item_author_name(self, item):
        return item.author.user.username

    def item_categories(self, item):
        return [tag.tag for tag in item.tagsList.all()]
