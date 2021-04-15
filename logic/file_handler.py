#!/usr/bin/python3
import os
from pathlib import Path

DIR_MAIN = '/NewsTest'
DIR_ARTICLES = DIR_MAIN + '/Articles'

def store_files():
    if not os.path.exists(home + DIR_ARTICLES):
        os.makedirs(home + DIR_ARTICLES)

def get_stored_articles():
    todo

def get_new_articles():
    todo

# private method only. Do not access from outside
def __delete_articles():
    todo



home = str(Path.home())
store_files()
