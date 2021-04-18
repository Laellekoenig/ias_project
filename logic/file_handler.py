#!/usr/bin/python3
import os
import glob
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
    file.write(article.get_json())
    file.close()

def get_article_by_path(path):
    article = Article(os.path.split(path)[1].split(' - ')[0]) # get News Source
    file = open(path, 'r')
    article.fill_article_from_json_file(file)
    file.close()
    return article



def get_article_list():
    return glob.glob(DIR_ARTICLES + '/*.json')

#def read_article():
    
# private method only. Do not access from outside
def __delete_articles():
    todo

store_files()
article_test = Article(NewsSource.SRF)
article_test.set_title_0("Article Title 0")
article_test.set_title_1("Article Title 1")
article_test.set_subtitle("Subtitle")
article_test.set_author("Hans Franz Sebastian Barthalomeus")
article_test.set_date_and_time("14:23, 18. April 2021")
article_test.add_paragraph("PARAGRAPH")
article_test.add_paragraph("PAR 2")
article_test.add_tagline("taglin text")
article_test.add_paragraph("Paragraph 3")
article_test.add_tagline("tagline number 2")
safe_article(article_test)
#print(article_test.get_html())
#print(get_article_list())
#a = get_article_by_path(get_article_list()[1])
#print(a.get_html())
