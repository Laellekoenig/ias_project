#!/usr/bin/python3
import os
from pathlib import Path
from article import Article, NewsSource

DIR_MAIN = str(Path.home()) + '/NewsTest'
DIR_ARTICLES = DIR_MAIN + '/Articles'

def store_files():
    if not os.path.exists(DIR_ARTICLES):
        os.makedirs(DIR_ARTICLES)

def get_stored_articles():
    todo

def get_new_articles():
    todo

def safe_article(article):
    source = article.news_source
    title = article.title_0
    file = open(DIR_ARTICLES + '/' + source + ' - ' + title + '.json', 'w')
    file.write(article.get_json_article())
    file.close()

#def read_article():
    
# private method only. Do not access from outside
def __delete_articles():
    todo


article_test = Article(NewsSource.DIE_ZEIT)
article_test.add_paragraph("PARAGRAPH")
article_test.add_paragraph("PAR 2")
article_test.add_tagline("taglin text")
article_test.add_paragraph("Paragraph 3")
article_test.add_tagline("tagline number 2")
article_test.set_title_0("test title")
safe_article(article_test)
store_files()
