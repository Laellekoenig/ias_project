from bs4 import BeautifulSoup
import requests
import re
from article import Article


def getURLsfromRSS():
    src = requests.get("https://www.srf.ch/news/bnf/rss/1646")

    #html content stored in scr
    html = src.content

    items = BeautifulSoup(html, 'html.parser').find_all('item')

    urls = list()
    for item in items:
        url = item.contents[2]
        urls.append(url)

    return urls

def getArticleFromURL(url):
    src = requests.get(url)
    html = src.content

    #parse src (often called soup)
    htmlParsed = BeautifulSoup(html, 'html.parser')

    categoryPattern = 'ch/(.+?)/(.+?)/'
    mainCategory = re.search(categoryPattern, url).group(1) # get 2 categories, for example 'news' and 'schweiz' or 'sport' and 'fussball'
    secondaryCategory = re.search(categoryPattern, url).group(2)

    overtitle = htmlParsed.find('span', class_='article-title__overline').text   #overline title of article
    title = htmlParsed.find('span', class_='article-title__text').text   # title of article

    content = htmlParsed.find('div', class_='article-content')  # all the content of the article-content class

    if content.find(class_ = "ticker-item") is None:    # only take article if it has no live ticker, otherwise ignore it

        # get the date the article got published and last modified (if there, otherwise let it be empty strings)
        if htmlParsed.find(class_='article-author__date') is not None:
            dates = str(htmlParsed.find(class_='article-author__date'))
            datePattern = '(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d).*(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d)'
            publishedDate = re.search(datePattern, dates).group(1)
            modifiedDate = re.search(datePattern, dates).group(2)

        else:
            publishedDate = ""
            modifiedDate = ""

        # get rid of polls
        if content.find(class_="poll__title") is not None:
            content.find(class_="poll__title").decompose()
            pollAnswer = content.find(class_="poll-option poll-option--poll")
            while pollAnswer is not None:
                content.find(class_="poll-option poll-option--poll").decompose()
                pollAnswer = content.find(class_="poll-option poll-option--poll")
            content.find(class_="js-poll_taken_text h-element--hide").decompose()
        
        # details of a person in the article, is removed
        if content.find('p', class_='person-details__name') is not None:
            content.find('p', class_='person-details__name').decompose()
        if content.find('p', class_='person-details__function') is not None:
            content.find('p', class_='person-details__function').decompose()
        
        if content.find_all('h2', class_='related-items-list__heading') is not None:
            for element in content.find_all('h2', class_='related-items-list__heading'):
                element.decompose()
            for rel in content.find_all(class_="related-items-list__item"):
                rel.parent.decompose()

        for a in content.find_all('a'):
            a.replaceWithChildren().text

        for span in content.find_all('span'):
                span.decompose()

        content = content.find_all(['p', 'h2', 'h3', 'li']) # take all <p>, <h2>, <h3> and <li> tags in the article-content class (all the relevant text in the article)

        newArticle = Article("SRF") #make a new article and fill it with the important informations
        newArticle.set_title_0(overtitle)
        newArticle.set_title_1(title)
        newArticle.set_date_and_time(publishedDate)
        #newArticle.set_date_and_time_updated(modifiedDate) not yet available
        
        for text in content:
            strText = str(text)
            if re.search("<li>", strText):
                print()
                #newArticle.add_li(text.text) not yet available method
            elif re.search("<p>", strText):
                newArticle.add_paragraph(text.text)
            elif re.search("<h2>", strText):
                newArticle.add_tagline(text.text)
            elif re.search("<h3>", strText):
                newArticle.add_tagline(text.text)

        return newArticle

    else:
        return None
       
def getSRFArticles():
    articleList = list()
    urls = getURLsfromRSS()

    for url in urls:
        if url is not None:
            article = getArticleFromURL(url)
            articleList.append(article)

    return articleList
    
def main():
    
    getSRFArticles()

if __name__ == "__main__":
    main()