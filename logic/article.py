from enum import Enum
import json

class NewsSource(str, Enum):
    SRF = 'SRF'
    DIE_ZEIT = 'Die Zeit'

# the html file is written with tags according to this class
class HTMLTag(str, Enum):
    TITLE_0 = 'h3'
    TITLE_1 = 'h1'
    SUBTITLE = 'h2'
    AUTHOR = 'h3'
    DATE_AND_TIME = 'h4'
    TAGLINE = 'h2'
    PARAGRAPH = 'p'

class Category(str, Enum):
    POLITICS = 'politics'
    GEO_POLITICS = 'geo_politics'
    SPORTS = 'sports'
    CULTURE = 'culture'
    TECHNOLOGY = 'technology'
    WEATHER = 'weather'
    OTHER = 'other'


class Article:
    def __init__(self, news_source):
        self.news_source = news_source
        self.category = Category.OTHER
        self.tags = []
        self.date_and_time_modified = ""
        self.bookmarked = False
        self.opened = False

        self.title_0 = ""
        self.title_1 = ""
        self.subtitle = ""
        self.author = ""
        self.date_and_time = ""
        self.content_index = []
        self.content = []

    def set_category(self, main_category):
        self.main_category = main_category

    def add_tag(self, tag):
        self.tags.append(tag)

    def set_title_0(self, title_0):
        self.title_0 = title_0
    
    def set_title_1(self, title_1):
        self.title_1 = title_1

    def set_subtitle(self, subtitle):
        self.subtitle = subtitle

    def set_author(self, author):
        self.author = author

    def set_date_and_time(self, date_and_time):
        self.date_and_time = date_and_time

    def set_date_and_time_modified(self, date_and_time_modified):
        self.date_and_time_modified = date_and_time_modified

    def add_tagline(self, tagline):
        self.content_index.append("tagline")
        self.content.append(tagline)

    def add_paragraph(self, paragraph):
        self.content_index.append("paragraph")
        self.content.append(paragraph)

    def fill_article_from_json_file(self, file):
        data = json.load(file)

        self.news_source = data['news_source']
        self.category = data['category']
        self.tags = data['tags']
        self.date_and_time_modified = data['date_and_time_modified']
        self.bookmarked = data['bookmarked']
        self.opened = data['opened']

        self.title_0 = data['title_0']
        self.title_1 = data['title_1']
        self.subtitle = data['subtitle']
        self.author = data['author']
        self.date_and_time = data['date_and_time']
        self.content_index = data['content_index']
        self.content = data['content']

    def get_content(self):
        return (content_index, content)
    
    def get_json(self):
        data = {}
        data['news_source'] = self.news_source
        data['category'] = self.category
        data['tags'] = self.tags
        data['date_and_time_modified'] = self.date_and_time_modified
        data['bookmarked'] = self.bookmarked
        data['opened'] = self.opened

        data['title_0'] = self.title_0
        data['title_1'] = self.title_1
        data['subtitle'] = self.subtitle
        data['author'] = self.author
        data['date_and_time'] = self.date_and_time
        data['content_index'] = self.content_index
        data['content'] = self.content
        
        json_file = json.dumps(data, indent = 4)
        return json_file

    def get_html(self):
        html = "<qt>\n<body>\n"
        html += self.get_tagged_string(HTMLTag.TITLE_0, self.title_0)
        html += self.get_tagged_string(HTMLTag.TITLE_1, self.title_1)
        html += self.get_tagged_string(HTMLTag.SUBTITLE, self.subtitle)
        html += self.get_tagged_string(HTMLTag.AUTHOR, self.author)
        html += self.get_tagged_string(HTMLTag.DATE_AND_TIME, self.date_and_time)

        i = 0
        for c in self.content_index:
            if c == 'tagline':
                html += self.get_tagged_string(HTMLTag.TAGLINE, self.content[i])
            elif c == 'paragraph':
                html += self.get_tagged_string(HTMLTag.PARAGRAPH, self.content[i])
            i += 1
        html += "</body>\n</qt>"
        return html

    def get_tagged_string(self, HTMLTag, str):
        return '<' + HTMLTag + '>' + str + '</' + HTMLTag + '>\n'