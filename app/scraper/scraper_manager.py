from SRFScraper import getSRFArticles
from logic.file_handler import get_articles

def get_new_articles_from_web():
    srf_articles = getSRFArticles(get_articles)