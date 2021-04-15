from bs4 import BeautifulSoup
import requests
import re


def getURLsfromRSS():
    src = requests.get("https://www.srf.ch/news/bnf/rss/1646")
    #print(src.status_code) # if 200, website was accessible

    #html of the website
    html = src.content

    items = BeautifulSoup(html, 'html.parser').find_all('item')
    #print(urls)

    f = open("URLs.txt", "w")
    for item in items:
        url = item.contents[2]
        f.write("{}{}".format("-", url))
        f.write('\n')

    f.close()   
    return items

def getarticleFormURL(url):
    src = requests.get(url)
    html = src.content

    #parse src (often called soup)
    htmlParsed = BeautifulSoup(html, 'html.parser')

    categoryPattern = 'ch/(.+?)/(.+?)/'
    mainCategory = re.search(categoryPattern, url).group(1) # get 2 categories, for example 'news' and 'schweiz' or 'sport' and 'fussball'
    secondaryCategory = re.search(categoryPattern, url).group(2)
    title = htmlParsed.find('span', class_='article-title__text')   # title of text

    content = htmlParsed.find('div', class_='article-content')

    # get rid of polls
    if content.find(class_="poll__title") is not None:
        content.find(class_="poll__title").decompose()
        pollAnswer = content.find(class_="poll-option poll-option--poll")
        while pollAnswer is not None:
            content.find(class_="poll-option poll-option--poll").decompose()
            pollAnswer = content.find(class_="poll-option poll-option--poll")
        content.find(class_="js-poll_taken_text h-element--hide").decompose()

    content = content.find_all(['p', 'h2', 'li']) # take all <p> and <h2> tags in the article-content class (all the relevant text in the article)

    #print("MAIN_CATEGORY:\n" + mainCategory + "\n")
    #print("SECONDARY_CATEGORY:\n" + secondaryCategory + "\n")
    #print("TITLE: \n")
    #print(title.text)
    #print("\nCONTENT: \n")

    #for text in content:
        #for tex in text.find_all('a'):
         #   tex.decompose()
        #for tex in text.find_all(class_="ticker-item__time")
        #    tex.decompose()
        #for tex in text.find_all(class_="ticker-item")
        #    tex.decompose()

        #not working
    #for text in content:
    #    li = text.find('li')
    #    if li is not None:
    #        text.text
    #    print("{}{}\n".format("-", text))

    articleContent = list()

    articleContent.append(mainCategory)
    articleContent.append(secondaryCategory)
    articleContent.append("<h2>" + title.text + "</h2>")

    for text in content:
        articleContent.append(text)

    return articleContent
       

def main():
    # if 200, website was accessible
    #result = requests.get("https://www.srf.ch/news/bnf/rss/1646")
    #print(result.status_code)

    #page content stored in scr
    #src = result.content
    #print(src)

    #soup = BeautifulSoup(src, 'html.parser')
    #print(soup)

    #f = open("text.html", "w")

    #title = soup.find('span', class_='article-title__text')

    #f.write("{}\n{} \n\n".format("<p>this is the title:</p>", title))

    #category = soup.find('div', class_='sharing-bar')
    #pattern = "data-share-category=\|(.*?)\|>"
    #substring = re.search(pattern, category).group(1)
    #print(category)

    #print(category)

    #content = soup.find('div', class_='article-content')

    #f.write("{}{} \n\n".format("this is the whole content in 'article-content':\n", content)) #all the content of the article-content class

    #print(content)
    #if (not content is None):
        #content = content.find_all(['p', 'h2']) #there will be more?
        #i = 0
        #f.write("<p>this is the content text splitted into separated parts between p or h2</p>\n")
        
       # for text in content:
          #  f.write("{}{}".format("-", text))
          #  f.write('\n')

    #f.close()   

    items = getURLsfromRSS() # TODO: function should return array or list of urls, not items!!
    f = open("articles.html", "w")
    f2 = open("articles.txt", "w")

    stopper = 0 #remove
    for item in items:

        if stopper >= 10: #remove
            break

        url = item.contents[2]
        articleContentList = getarticleFormURL(url)
        for article in articleContentList:
            f.write("{}".format(article))
            f2.write("{}".format(article))

        stopper += 1 #remove

    f.close()
    f2.close()

if __name__ == "__main__":
    main()