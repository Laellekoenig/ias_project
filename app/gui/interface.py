import threading
from scraper.srf_scraper import getSRFArticles
from logic.article import Article

class Interface:

    def __init__(self, window):
        self.window = window
        self.article_list = None
        self.article_titles = None
        self.is_downloading = False

    # returns a list of all downloaded article files
    def get_downloaded_articles(self):
        if self.article_titles == None:
            return []
        return self.article_titles

    def threaded_download(self):
        if not self.is_downloading:
            self.window.switch_to_loading()
            thread = threading.Thread(target=self.download)
            thread.start()
        else:
            print("already downloading")

    def download(self):
        self.is_downloading = True
        articles = getSRFArticles()
        self.article_list = articles
        titles = []

        for article in articles:
            if article is not None:
                titles.append(article.title_0)

        self.article_titles = titles
        self.is_downloading = False
        print("finished downloading")

    def get_article_html_by_title(self, title):
        if self.article_titles == None:
            return ""

        for article in self.article_list:
            if article != None and article.title_0 == title:
                return article.get_html()
