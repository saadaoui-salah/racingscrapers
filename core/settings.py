# Scrapy settings for core project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from dotenv import load_dotenv;load_dotenv()
import os

BOT_NAME = "core"

SPIDER_MODULES = ["core.spiders"]
NEWSPIDER_MODULE = "core.spiders"

ADDONS = {}

# Dropbox Auth
DROPBOX_ACCESS_TOKEN = "sl.u.AGFyexNKtmLt3ZdI4NyQT3zhG4ZX9nAB8-MiIMcqwCOFw3fLaLKQ5DDpKDmhbUy9vhmx_iex_YeqYG51SCikH13jxdZNij3i5u0DFQ7SrGzDyBEY-XAiB1n29qNeAecA-oJaKyKI_6LonklzOXUqGNmQeL8xYhuKPsOpZqgOFWpWrmbtNd1LGilEYZMPvgV5vdT7IwB4fQxzoKE22FXg2XGO0SNahIijgVJ45kiGH1_ebeKTezy95jLWBgHu8sp6mK62TuQkuSSZY2WyMlhWSRIPsLn8sAY3P3YUQkxfiAuDAmX8hsEEFMiWeVny_UJCNrtz04BfaqRK22aSCo0RW5JFNBx00mG1x3ZhVDLqC2eRa91FlvUI-WiAGZsnHvgBVU8MFylspHU_1MgOLmdc66szGiLTSyGmuR-mXoYuaftmXwbSM6xYGHxs5_YQNcbwSoe4Bq3G6wHWOJHfFdEGZTLrOwS8nEz2lvGk7yC8eeSAvszYD6esjHfJQBqVOH6eXZl1eI3mm6LLbrsC1ulIwy6G9_k-5hF4NKU-v6ILK8axnQNn_tma2G3iQ9OmauFf1UN34__XIgBFLgo10VGrkGjdcdYY6Huc_Ntae-rAVyop5Uth8JeQ0CjoimbLhxab0o1cWOXBg-5xd48tIJjSa41qOGKPbTc3Gq7RdgF8Vm3MhTbajKCua6MntUDckU_JbvyWZIoyTAmXlbhURPMnhfK2pxor9xsPQbFWyGCc68nT2DS9gk3NOXSOitIauiP2Lo_lLYPSmfTMDk-348llKj5QNbnbGv_AUmxvrDTSV9bR4OVDRJUUdzjMu8VqZFh7SWZg2c56S4f54Rl9Dfr4AENOugPRAA_68n6xGALk28SX27C1leLn96nC_9ZhlTlCass-dj1doG9W_mypcjNrR8WiRL7ar9wkUNnIL1FPeikWUH68grRwYBuw9ZHOU050Yxhw3d1STiJ48287pUMF39I4SwDavwk1QpU85N6QYyQjWEMr16xwlQBHBbu2q9pjydORyAV9PLRMG0HePMH_5oK8WF9JlRhEerk7dzKJ6Kwa_zf5nuggt8BOoA88seFmB6hzF-lCZTx6gSI1Xm-uxkir5A2bB4a3N6iq1ludl9hSKo0jr64Z4V3HCn4CrE233pnAMVKvh-DIG-audDyWGguiYM6zLxXnNbiQFnwCbbDiDC0mzMbqHRmgpOiYXOsCeX0MrvhvjqxygIP2KUDd0tX91HWhBdGVt0AxcesMIj9g-S5iWOYkJ7uSOokYgLjRZqXvyYqmQmHnAPDYB-IpWV4n"  # From Dropbox App Console

# Local file produced by Feed Exporters
UPLOAD_FILE_PATH = "export.csv"  # Make sure your FEEDS produces this

# Remote Dropbox path (optional)
DROPBOX_UPLOAD_PATH = "/DataBricks/Q%20Straight/export.csv"

EXTENSIONS = {
    "core.extensions.S3UploadExtension": 500,
}

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')           # replace with environment variable
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')     # replace with environment variable

UPLOAD_FILE_PATH = "export.csv"

S3_BUCKET = "databricks-workspace-stack-7a672-bucket"
S3_PREFIX = "unity-catalog/652267796750120/CSV/"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "core (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

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
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "core.middlewares.CoreDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "core.pipelines.CorePipeline": 300,
#}

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
FEED_EXPORT_ENCODING = "utf-8"
