BOT_NAME = "pageskip"

SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"

USER_AGENT = "pageskip/0.1.0 (EPSEVG STIC ticket indexing spider) (+https://github.com/pol-epsevg/pageskip)"
COOKIES_ENABLED = True

# There's no robots.txt on the ticket website
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS_PER_DOMAIN = 8
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 15
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0

# HTTPCACHE_ENABLED = True # Disabled for debugging
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [403, 404, 500]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

LOG_LEVEL = 'DEBUG'

FEED_EXPORT_ENCODING = "utf-8"
FEEDS = {
    'tickets_output.json': {
        'format': 'json',
        'overwrite': True
    }
}
