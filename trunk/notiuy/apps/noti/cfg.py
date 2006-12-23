# Asbolute URL base path where Noti will be running 
httphost = 'beta.notiuy.com'
urlbase = ''

# The site name. This is the title displayed in main pages, feeds, and such
sitename = 'NotiUY 2.0 beta'
tagline = 'Todas las noticias uruguayas en un solo sitio'

# The template to use. You can use this to localize Noti in your 
# own language. Supported languages are en and es. Comment out this 
# if you don't have gettext support enabled in php. It's highly
# recommended to use a full locale (like en_ES or en_US) to avoid 
# compatibilty problems. Also, remember to add ".UTF-8" suffix for non
# english languages

language = 'en_US'
#language = 'es_ES.UTF-8'

# Format to use for displaying dates, in strftime syntax
dateformat = '%d %B %Y'

#<!-- Format to use for displaying times, in strftime syntax -->
#<!-- 24 hour format
#timeformat = '%H:%M'
# <!-- 12 hour AM/PM format
timeformat = '%I:%M %p'

# Time zone to use. Comment out this if you want to use the server 
# local time zone -->
# <timezone>America/Sao_Paulo</timezone>
timezone = "America/Montevideo"

#  The list of users allowed to administer this site 
#     (this is a space separated list)
admins = ['admin', 'prh']

#  The list of users allowed to upload news XML data via postnews.php
#       (this is a space separated list)
uploaders = ['crawler', 'prh']

#  Whether to show the time it takes to server each page at the end of 
#  page. Used to measure performance and debugging purposes. Comment
#  to disable (or in doubt). Possible values are:
#  * inline: show served time at the end of the page
#  * comment: output served as HTML comment (won't display on the page) 
#
# runtimer = 'inline'

#  Days to remember user when they check "Remember me"
remember_user_days = 30

# Never return more than this number of articles in one shot
query_max_articles = 200

# Tag clouds font size constraints
tagcloud_maxsize = 28
tagcloud_minsize = 12

# Maximum number of articles per section (for multisection pages)
section_max_articles = 10

# Maximium number of articles in paged results
articles_per_page = 15

# Maximum number of pages
max_pages = 15

# Absolute maximuum of articles fetched in one shot
search_max_articles = 150

# Ranking of a note to achieve the status "popular"
popular_threshold = 2
popular_max_articles = 100

#  The number of minutes the feed readers shuold cache the content.
#  A value of 720 (12 hs) should be fine if news gets updates once a 
#  day. This value must be non-zero for the feed to conform to the
#  standards -->
feed_ttl = 30

#  The absolute maximum number of notes per feed. This restriction applies
#  for all feed (including user subscriptions) and supersedes the user 
#  preferences. Warning: setting this number too high (50+) may cause 
#  bandwidth overconsumption -->
feed_max_notes = 30

#  Sender address to use for sending daily news mails -->
mail_from = 'noti@notiuy.com'

#  Web host to use when sending emails (since it can not be determined 
#  when running php from command line  -->
mail_httphost = 'notiuy.com'

# Crawlers configuration

# Enabled crawlers
crawlers = ['observa', 'elpais', 'espectador', 'larepublica', 'ultimasnoticias', 'montevideo'] 

# Timeout (in seconds) that fetchnews should wait for the web page response
timeout = 20

# How many times should we try to reconnect to news sites
retries = 3

