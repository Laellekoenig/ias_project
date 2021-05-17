#!/usr/bin/python3
import os
import glob
from pathlib import Path
from logic.article import Article, NewsSource
import re
import zipfile
from datetime import datetime
from datetime import timedelta
import time

DIR_MAIN = str(Path.home()) + '/NewsTest'
DIR_ARTICLES = DIR_MAIN + '/Articles'
DIR_EXPORT = DIR_MAIN + '/Export'
DELTA_TIME_OLDEST_ARTICLES = timedelta(days = 10)

def make_dirs():
    if not os.path.exists(DIR_ARTICLES):
        os.makedirs(DIR_ARTICLES)
    if not os.path.exists(DIR_EXPORT):
        os.makedirs(DIR_EXPORT)

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

def get_articles_with_paths():
    articles = []
    for path in glob.glob(DIR_ARTICLES + '/*.json'):
        articles.append((get_article_by_path(path), path))
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

# takes an argument of type 'datetime' or string in iso format
# creates a zip file containing all articles that are newer than the given time or the current time - delta time
# (whichever is later) in the export directory
# if no article is in specified time frame, no zip file is created
# returns path to created zip file or None
def zip_articles(date_time):
    if type(date_time) is str:
        date_time = datetime.fromisoformat(date_time)
    make_dirs()
    list_to_zip = []
    # if newest update of client is older than the specified deltatime, only newer articles than deltatime will be sent
    if date_time < datetime.fromtimestamp(time.time()) - DELTA_TIME_OLDEST_ARTICLES:
        date_time = datetime.fromtimestamp(time.time()) - DELTA_TIME_OLDEST_ARTICLES
    for article in get_articles_with_paths():
        ### handle articles with strange time stamp
        if '+' in article[0].date_and_time:
            continue
        if datetime.fromisoformat(article[0].date_and_time) > date_time:
            list_to_zip.append(article)

    if len(list_to_zip) == 0:
        print("No articles in specified time found.")
        return None
    zip_path = DIR_EXPORT + '/' + get_newest_datetime().isoformat() + '.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipF:
        ### only zip files not folder hyrarchy
        for article in list_to_zip:
            zipF.write(article[1], article[1].split('/')[-1], compress_type=zipfile.ZIP_DEFLATED)
    return zip_path

# returns the date and time of the newest article as 'datetime' type
def get_newest_datetime():
    date_time = None
    for article in get_articles():
        if '+' in article.date_and_time:
            continue
        if date_time == None:
            date_time = datetime.fromisoformat(article.date_and_time)
        elif datetime.fromisoformat(article.date_and_time) > date_time:
            date_time = datetime.fromisoformat(article.date_and_time)
    return date_time


#print(article_test.get_html())
#print(get_article_list())
#a = get_article_by_path(get_article_list()[1])
#print(a.get_html())
