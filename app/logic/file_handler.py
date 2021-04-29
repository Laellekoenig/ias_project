#!/usr/bin/python3
import os
import glob
from pathlib import Path
from logic.article import Article, NewsSource
import re

DIR_MAIN = str(Path.home()) + '/NewsTest'
DIR_ARTICLES = DIR_MAIN + '/Articles'

def make_dirs():
    if not os.path.exists(DIR_ARTICLES):
        os.makedirs(DIR_ARTICLES)

def get_stored_articles():
    #todo
    pass

def get_new_articles():
    #todo
    pass

def save_article(article):
    make_dirs()
    source = article.news_source
    title = article.title_1

    file_path = None
    if not article.path:
        file_path = DIR_ARTICLES + '/' + source + ' - ' + remove_incompatible_chars(title) + '.json'
    else:
        file_path = article.path
    file = open(file_path, 'w')
    file.write(article.get_json())
    file.close()

def remove_incompatible_chars(title):
    title = re.sub('[/\?%*:|"<>.,;=]', '', title)
    return title

def get_article_by_path(path):
    article = Article(os.path.split(path)[1].split(' - ')[0]) # get News Source
    file = open(path, 'r')
    article.path = path
    article.fill_article_from_json_file(file)
    file.close()
    return article

def get_articles():
    articles = []
    for path in glob.glob(DIR_ARTICLES + '/*.json'):
        articles.append(get_article_by_path(path))
    return articles

def get_article_titles():
    list = []
    for a in get_articles():
        list.append(a)
    return list

#def read_article():
    
def mark_as_deleted(article):
    article.deleted = True
    save_article(article)

# private method only. Do not access from outside
def delete_article(article):
    if type(article) is Article:
        os.remove(article.path)
    else:
        print("article '" + article + "' could not be removed")

#print(article_test.get_html())
#print(get_article_list())
#a = get_article_by_path(get_article_list()[1])
#print(a.get_html())
