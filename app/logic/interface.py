#!/usr/bin/python3
from logic.file_handler import get_articles
from logic.file_handler import save_article
from logic.file_handler import get_article_titles
from logic.article import Article
from scraper.srf_scraper import getSRFArticles
from scraper.scraper_manager import get_new_articles_from_web
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
        articles = get_new_articles_from_web()
        for article in articles:
            if article is not None:
                save_article(article)
        print("finished downloading")
        self.is_updating = False

    def get_articles(self):
        return get_articles()

    def get_article_titles(self):
        list = get_article_titles()
        return [x.title_1 for x in list]

    def get_article_html_by_title1(self, title):
        for article in self.get_articles():
            if article.title_1 == title:
                return article.get_html()

    def mark_as_deleted(self, article):
        article.deleted = True
        save_article(article)
    
    def mark_as_opened(self, article):
        article.opened = True
        save_article(article)

    def bookmark_article(self, article):
        article.bookmarked = True
        save_article(article)