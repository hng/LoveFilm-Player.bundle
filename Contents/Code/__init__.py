import re
import lovefilm

VIDEO_PREFIX = "/video/lovefilm-player"

NAME = "LoveFilm Player"

ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_SEARCH = 'icon-search.png'

RE_THUMB = Regex('UR(?P<x>[0-9]+),(?P<y>[0-9]+)_')
THUMB_PATTERN = 'packshot._UR%s,%s'

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
            season = int(season_details[1].replace('Series', '').strip())

            oc.add(SeasonObject(
                key = Callback(BrowseSeason, title = details["title"], season_url = details["url"]),
                rating_key = details["url"],
                show = show,
                index = season,
                title = details["title"],
                thumb = details["thumb"]))

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

@route("/video/lovefilm-player/tv/")
def BrowseSeason(title, season_url):
    oc = ObjectContainer(title2 = title)

    page = HTML.ElementFromURL(season_url)


    #for episode in page.xpath("//div[@class = 'list_episodes']"):



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
        match = RE_THUMB.search(original_url).groupdict()
        new_url = original_url.replace(THUMB_PATTERN % (match['x'], match['y']), THUMB_PATTERN % (match['x'] + '0', match['y'] + '0'))
        thumbs = [new_url] + thumbs
    except: pass

    Log("IABI")
    Log(thumbs)

    return thumbs
