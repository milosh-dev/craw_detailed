import os
# Scrapy settings for auto24 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "auto24"

SPIDER_MODULES = ["auto24.spiders"]
NEWSPIDER_MODULE = "auto24.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "auto24 (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "auto24.middlewares.Auto24SpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "auto24.flaresolverr.middlewares.FlareSolverrRetryMiddleware": 542,
    "auto24.flaresolverr.middlewares.FlareSolverrRedirectMiddleware": 541,
#    "auto24.flaresolverr.middlewares.FlareSolverrGetSolutionStatusMiddleware": 540,
#    "auto24.middlewares.Auto24DownloaderMiddleware": 543,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
}

#DOWNLOAD_HANDLERS = {
#    "http": "scrapy_impersonate.ImpersonateDownloadHandler",
#    "https": "scrapy_impersonate.ImpersonateDownloadHandler",
#}
#TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#     "auto24.pipelines.AutoPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

COOKIES_DEBUG = True

# FLARESOLVERR
# URL of the FlareSolverr proxy server
FLARESOLVERR_URL = "http://localhost:8191/v1"           #os.getenv("FLARESOLVERR_URL")
MY_SESSION_ID = "0073b137-efe9-495d-a1a2-1541f0791007"  #os.getenv("MY_SESSION_ID")
# How many sessions we will create
FLARESOLVERR_NR_SESSIONS = 3
# Timeout for Flaresolverr
FLARESOLVERR_TIMEOUT = 60000

# Enable and configure retry middleware
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.retry
RETRY_ENABLED = True
# Maximum number of times to retry, in addition to the first download.
RETRY_TIMES = 4
# Which HTTP response codes to retry.
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 404, 408, 429]
