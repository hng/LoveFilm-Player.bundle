import re
import lovefilm

VIDEO_PREFIX = "/video/lovefilm-player"

NAME = "LoveFilm Player"

ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

RE_TV_EPISODES = [
    Regex("^(?P<show>[^-]*) - S(?P<season_index>\d+) E(?P<episode_index>\d+) - (?P<episode_name>.*)$"),
    Regex("^(?P<show>[^-]*) - S(?P<season_index>\d+) E(?P<episode_index>\d+)$")
]

####################################################################################################
def Start():
    
    # Initialize the plugin
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")
    
    # Setup the artwork associated with the plugin
    ObjectContainer.title1 = NAME
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = 'InfoList'

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    MovieObject.thumb = R(ICON)
    MovieObject.art = R(ART)
    SeasonObject.thumb = R(ICON)
    SeasonObject.art = R(ART)
    NextPageObject.thumb = R(ICON)
    NextPageObject.art = R(ART)

    # Cache HTTP requests for up to a day
    HTTP.CacheTime = CACHE_1DAY

####################################################################################################

def MainMenu():
    oc = ObjectContainer(no_cache = True)

    for hotlist_item_id in lovefilm.ordered_hot_lists:
        hotlist_item = lovefilm.hot_lists[hotlist_item_id]
        oc.add(DirectoryObject(
            key = Callback(BrowseHotlist, id = hotlist_item_id),
            title = hotlist_item.title))

    if Prefs['site'] == "UK":
        oc.add(DirectoryObject(key = Callback(BrowseGenres, title = "Genres"), title = "Genres"))

    # Preferences
    oc.add(PrefsObject(title = L('Preferences')))
    
    return oc

####################################################################################################

@route("/video/lovefilm-player/hotlist/{id}")
def BrowseHotlist(id):
    hotlist_item = lovefilm.hot_lists[id]
    return BrowseURL(hotlist_item.title, hotlist_item.browse_url())

####################################################################################################

@route("/video/lovefilm-player/genres")
def BrowseGenres(title):
    oc = ObjectContainer(title2 = title)

    for genre_item_id in lovefilm.ordered_genre_list:
        genre_item = lovefilm.genre_lists[genre_item_id]
        oc.add(DirectoryObject(
            key = Callback(BrowseURL, title = genre_item.title, url = genre_item.browse_url()),
            title = genre_item.title))

    return oc

####################################################################################################

@route("/video/lovefilm-player/browse")
def BrowseURL(title, url):
    oc = ObjectContainer(title2 = title)

    page = HTML.ElementFromURL(url)
    for item in page.xpath("//div[@id = 'main-content']//div[contains(@class, 'film_listing')]"):

        details = ParseItem(item)
        if details["type"] == "Film":
            oc.add(MovieObject(
                url = details["url"],
                title = details["title"],
                summary = details["summary"],
                thumb = Resource.ContentsOfURLWithFallback(GetThumbList(details['thumb']), fallback = ICON),
                genres = details["genres"],
                year = details["year"],
                directors = details["directors"],
                rating = details["rating"],
                content_rating = details["content-rating"]))

        elif details["type"] == "TV":

            season_details = details["title"].split('-')
            show = season_details[0].strip()

            oc.add(TVShowObject(
                key = Callback(BrowseShow, title = details["title"], show_url = details["url"]),
                rating_key = details["url"],
                title = show,
                thumb = Resource.ContentsOfURLWithFallback(GetThumbList(details['thumb']), fallback = ICON)))

    pagination = page.xpath("//div[contains(@class, 'pagination')]")
    if len(pagination) > 0:
        next = pagination[0].xpath(".//a[contains(text(), 'Next')]")
        if len(next) > 0:
            url = next[0].get('href')
            oc.add(NextPageObject(
                key = Callback(BrowseURL, title = title, url = url),
                title = "More..."))
    return oc

####################################################################################################

@route("/video/lovefilm-player/tv")
def BrowseShow(title, show_url):
    oc = ObjectContainer(title2 = title)

    page = HTML.ElementFromURL(show_url)
    
    show = page.xpath("//meta[@property = 'og:title']")[0].get('content').split('-')[0].strip()
    thumb = page.xpath("//meta[@property = 'og:image']")[0].get('content')
    thumbs = [thumb.replace('medium', 'large'), thumb]

    for season in page.xpath("//div[contains(@class, 'season')]/div[@class = 'left_col']//li/a"):

        season_url = season.get('href')
        if season_url.startswith('/'):
            season_url = show_url.split('/tv')[0] + season_url

        title = season.xpath(".//span[@class = 'n_season']/text()")[0]

        index = None
        try: index = int(re.search('([0-9]+)', title).groups()[0])
        except: pass

        episode_count = None
        try: episode_count = int(re.search('([0-9]+)', season.xpath('.//span[@class = "n_episodes"]/text()')[0]).groups()[0])
        except: Log.Exception("BOOM")

        oc.add(SeasonObject(
            key = Callback(BrowseSeason, title = title, season_url = season_url),
            rating_key = season_url,
            show = show,
            title = title,
            index = index,
            episode_count = episode_count,
            thumb = Resource.ContentsOfURLWithFallback(thumbs, fallback = ICON)))

    if len(oc) != 1:
        return oc
    return BrowseSeason(title = title, season_url = show_url)

####################################################################################################

@route("/video/lovefilm-player/tv/season")
def BrowseSeason(title, season_url):
    oc = ObjectContainer(title2 = title)

    page = HTML.ElementFromURL(season_url)

    thumb = page.xpath('//div[@class = "heroshot"]/img')[0].get('src')

    for episode in page.xpath("//div[@class = 'list_episodes']//li"):
        
        index = int(episode.xpath(".//span[@class = 'episode_index']/text()")[0])
        
        episode_link = None
        try: episode_link = episode.xpath(".//a[@class = 'episode_link']")[0]
        except: episode_link = episode.xpath(".//span[@class = 'episode_link']")[0]

        url = episode_link.get('href')
        if url == None:
            url = season_url

        full_title = episode_link.text

        show = None
        season_index = None
        episode_index = None
        episode_name = None

        for pattern in RE_TV_EPISODES:
            match = pattern.match(full_title)
            if match != None:
                match_dict = match.groupdict()
                if match_dict.has_key('show'):
                    show = match_dict['show']
                if match_dict.has_key('season_index'):
                    season_index = int(match_dict['season_index'])
                if match_dict.has_key('episode_index'):
                    episode_index = int(match_dict['episode_index'])
                if match_dict.has_key('episode_name'):
                    episode_name = match_dict['episode_name']

        if show == None:
            episode_name = full_title

        oc.add(EpisodeObject(
            url = url,
            title = episode_name,
            show = show,
            season = season_index,
            index = episode_index,
            thumb = Resource.ContentsOfURLWithFallback(GetThumbList(thumb), fallback = ICON)))

    return oc

####################################################################################################

def ParseItem(item):
    details = {}
    
    core_info = item.xpath(".//div[contains(@class, 'core_info')]")[0]
    details["type"] = core_info.get('data-product_type')
    details["title"] = core_info.get('data-product_name')
    details["genres"] = [ g.strip() for g in core_info.get('data-genre_names').split(';') ]

    details["url"] = item.xpath(".//a")[0].get('href')
    details["thumb"] = item.xpath(".//img")[0].get('src')
    details["year"] = int(item.xpath(".//span[@class = 'release_decade']/text()")[0].strip())
    details["summary"] = item.xpath(".//div[contains(@class, 'synopsis')]/p/text()")[0].strip()
    details["directors"] = item.xpath(".//th[contains(text(), 'Directors:')]/../td/a/text()")

    try: details["rating"] = float(item.xpath(".//span[contains(@class, 'star-rating')]")[0].get('data-current_rating')) * 2
    except: details["rating"] = None

    try: details["content-rating"] = item.xpath(".//span[contains(@class, 'cert')]/text()")[0].strip()
    except: details["content-rating"] = ""

    return details

####################################################################################################

def GetThumbList(original_url):
    thumbs = [original_url]

    try:
        new_url = None
        for splitter in ['packshot', 'fourthree']:
            separate = original_url.split(splitter)
            if len(separate) == 2:
                new_url = separate[0] + splitter + '.jpg'
                break

        if new_url != None:
            thumbs = [new_url] + thumbs
    except: pass

    return thumbs
