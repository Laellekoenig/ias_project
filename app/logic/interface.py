#!/usr/bin/python3
from logic.file_handler import get_articles
from logic.file_handler import save_article
from logic.file_handler import get_article_titles
from logic.file_handler import delete_article
from logic.article import Article
from scraper.srf_scraper import getSRFArticles
import threading
class LogicInterface:
    def __init__(self):
        self.is_updating = False

    def download_new_articles(self):
        # TODO only download new articles
        if not self.is_updating:
            self.is_updating = True
            thread = threading.Thread(target=self.start_scraping)
            thread.start()

    def start_scraping(self):
        articles = getSRFArticles()
        for article in articles:
            if article is not None:
                save_article(article)
        self.is_updating = False

    def get_articles(self):
        return get_articles()

    def get_article_titles(self):
        return get_article_titles()

    # deletes every article in the given article list
    def delete_articles(self, articles):
        for article in articles:
            delete_article(article)
    
