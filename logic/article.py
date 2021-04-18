from enum import Enum
import json

class NewsSource(str, Enum):
    SRF = 'SRF'
    DIE_ZEIT = 'Die Zeit'

class Article:
    def __init__(self, news_source):
        self.news_source = news_source
        self.date_and_time_updated = ""
        self.bookmarked = False
        self.opened = False

        self.title_0 = ""
        self.title_1 = ""
        self.subtitle = ""
        self.author = ""
        self.date_and_time = ""
        self.content_index = []
        self.content = []

    
    def set_title_0(self, title_0):
        self.title_0 = title_0
    
    def set_title_1(self, title_1):
        self.title_1 = title_1

    def set_subtitle(self, subtitle):
        self.subtitle = subtitle

    def set_author(self, author):
        self.author = author

    def set_time_and_date(self, time_and_date):
        self.time_and_date = time_and_date

    def add_tagline(self, tagline):
        self.content_index.append("tagline")
        self.content.append(tagline)

    def add_paragraph(self, paragraph):
        self.content_index.append("paragraph")
        self.content.append(paragraph)

    # private method
    def get_next_content(self):
        if len(self.content_index) <= 0:
            return "empty"
        content_type = self.content_index.pop(0)
        return (content_type, self.content.pop(0))
    
    def get_json_article(self):
        data = {}
        data['news_source'] = self.news_source
        data['date_and_time_updated'] = self.date_and_time_updated
        data['bookmarked'] = self.bookmarked
        data['opened'] = self.opened
        data['title_0'] = self.title_0
        data['title_1'] = self.title_1
        data['subtitle'] = self.subtitle
        data['author'] = self.author
        data['date_and_time'] = self.date_and_time
        data['content'] = []
        data['content_index'] = []
        while True:
            content = self.get_next_content()
            if content == "empty":
                break
            data['content_index'].append(content[0])
            data['content'].append(content[1])

        
        
        json_file = json.dumps(data, indent = 4)
        return json_file
