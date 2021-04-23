from scraper.srf_scraper import getSRFArticles
from logic.article import Article

class Interface:

    def __init__(self):
        pass

    def getDownloadedArticles(self):
        return ["test", "blabla", "tada"]

    def download(self):
        articles = getSRFArticles()
        titles = []

        for article in articles:
            if article is not None:
                titles.append(article.title_0)

        return titles
