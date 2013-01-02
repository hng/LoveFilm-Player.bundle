
class Catalog(object):
    def __init__(self, title, formats):
        self.title = title
        self.formats = formats

        self.url = "/catalog/video".replace('/', '%2F')
        self.unique = "series"
        self.mature = "1"
        self.type = "series OR feature OR film"
        self.adult = "0"

    def browse_url(self):
        type = String.Quote(self.type, usePlus = True)

        formats = ""
        for f in ["_fmt|digital"] + self.formats:
            if len(formats) > 0:
                formats = formats + "&"
            formats = formats + "f=" + String.Quote(f, usePlus = True)

        token = "?u=%s" % self.url
        token = token + String.Quote("?unique=%s&mature=%s&type=%s&%s&adult=%s&m=GET" % (self.unique, self.mature, type, formats, self.adult))
        token = String.Quote(token)
        token = String.Quote(token)
        return "http://www.lovefilm.com/browse/?token=%s&v=l&r=25" % token

hot_lists = {
  "newreleases":  Catalog("New Releases", ["hotlist|new_releases"]),
  "justadded":    Catalog("Just Added", ["hotlist|re_releases"]),
  "mostwatched":  Catalog("Most Watched", ["hotlist|most_watched"])
}

ordered_hot_lists = ["newreleases", "justadded", "mostwatched"]

genre_lists = {
    "actionadventure":  Catalog("Action/Adventure", ["genre|6095"]),
    "animated":         Catalog("Animated", ["genre|7234"]),
    "anime":            Catalog("Anime", ["genre|7338"]),
    "bollywood":        Catalog("Bollywood", ["genre|6104"]),
    "children":         Catalog("Children", ["genre|6097"]),
    "comedy":           Catalog("Comedy", ["genre|6098"]),
    "documentary":      Catalog("Documentary", ["genre|6099"]),
    "drama":            Catalog("Drama", ["genre|6100"]),
    "family":           Catalog("Family", ["genre|6101"]),
    "gay":              Catalog("Gay/Lesbian", ["genre|6223"]),
    "horror":           Catalog("Horror", ["genre|6103"]),
    "music":            Catalog("Music/Musical", ["genre|6105"]),
    "romance":          Catalog("Romance", ["genre|6106"]),
    "scifi":            Catalog("Sci-Fi/Fantasy", ["genre|6107"]),
    "special":          Catalog("Special Interest", ["genre|6200"]),
    "sport":            Catalog("Sport", ["genre|6108"]),
    "teen":             Catalog("Teen", ["genre|7539"]),
    "television":       Catalog("Television", ["genre|6186"]),
    "thriller":         Catalog("Thriller", ["genre|6109"]),
    "world":            Catalog("World Cinema", ["genre|6102"]),
    "adult":            Catalog("Adult", ["genre|6096"])
}

ordered_genre_list = ["actionadventure", "animated", "anime", "bollywood", "comedy", "documentary", "drama",
                      "family", "gay", "horror", "music", "romance", "scifi", "special", "sport", "teen",
                      "television", "thriller", "world", "adult"]