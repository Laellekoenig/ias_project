from bs4 import BeautifulSoup
import requests
import re
from logic.article import Article

import time

# old_articles_infos are the titles, published- and modified dates from the articles that already have been saved before
def getURLsfromRSS(old_article_infos):
    src = requests.get("https://www.srf.ch/news/bnf/rss/1646")

    #html content stored in scr
    html = src.content

    items = BeautifulSoup(html, 'html.parser').find_all('item')

    rss_titles = list()
    urls = list()
    for item in items:
        title = item.contents[0]
        if title not in rss_titles: # not a duplicate title in rss feed
            rss_titles.append(title)
            if title not in old_article_infos[0]:
                url = item.contents[2]
                urls.append(url)
            else:
                pass    # TODO? would be implemented when updating articles is considered (currently not working with published- and modified date, would have to scrap whole html for this)
        #else:
        #    print(title)

    return urls

# get the one article found at the given url (only working for srf articles)
def getArticleFromURL(url):
    src = requests.get(url)
    html = src.content

    #parse src (often called soup)
    htmlParsed = BeautifulSoup(html, 'html.parser')

    categoryPattern = 'ch/(.+?)/(.+?)/'
    mainCategory = re.search(categoryPattern, url).group(1) # get 2 categories, for example 'news' and 'schweiz' or 'sport' and 'fussball'
    secondaryCategory = re.search(categoryPattern, url).group(2)

    overtitle = htmlParsed.find('span', class_='article-title__overline').text   # overline title of article
    title = htmlParsed.find('span', class_='article-title__text').text   # title of article

    content = htmlParsed.find('div', class_='article-content')  # all the content of the article-content class

    if content.find(class_ = "ticker-item") is None:    # only take article if it has no live ticker, otherwise ignore it

        # get the date the article got published and last modified (if there, otherwise let it be empty strings)
        publishedDate = None
        modifiedDate = None
        if htmlParsed.find(class_='article-author__date') is not None:
            dates = str(htmlParsed.find(class_='article-author__date'))
            datePattern = '(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d).*(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d)'
            publishedDate = re.search(datePattern, dates).group(1)
            modifiedDate = re.search(datePattern, dates).group(2)

        if publishedDate is None:
            publishedDate = "0000-01-01T01:01:00+02.00"
        if modifiedDate is None:
            modifiedDate = "0000-01-01T01:01:00+02.00"
            
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
                pass
                #newArticle.add_li(text.text) not yet available method
            elif re.search("<p>", strText):
                newArticle.add_paragraph(text.text)
            elif re.search("<h2>", strText):
                newArticle.add_tagline(text.text)
            elif re.search("<h3>", strText):
                newArticle.add_tagline(text.text)

        return newArticle

    else:
        #print(title)
        return None
       
# old_articles are the articles saved before (with the last time articles got downloaded)
def getSRFArticles(old_articles):
    articleList = list()
    infos = get_article_infos(old_articles)

    urls = getURLsfromRSS(infos)
    

    print("#URLs: " + str(len(urls)))

    for url in urls:
        if url is not None:
            article = getArticleFromURL(url)
            if article is not None:
                articleList.append(article)

    return articleList

def get_article_infos(articles): # articles is a list of articles
    infos = [[], [], []] # save title, published- and modified date of articles
    for article in articles:
        title = article.title_1
        published_date = article.date_and_time
        modified_date = article.date_and_time_modified
        if title is not None and published_date is not None and modified_date is not None:
            infos[0].append(title)
            infos[1].append(published_date)
            infos[2].append(modified_date)

    return infos    
    
def main():
    
    start = time.time()
    articles = getSRFArticles([])
    print("#Articles: " + str(len(articles)))
    print(time.time() - start)

if __name__ == "__main__":
    main()