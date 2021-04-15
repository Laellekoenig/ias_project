from bs4 import BeautifulSoup
import requests
import re

def main():
    # if 200, website was accessible
    result = requests.get("https://www.srf.ch/news/schweiz/corona-lockerungen-forderung-des-arbeitgeber-praesidenten-vogt-zieht-kreise")
    #print(result.status_code)

    #page content stored in scr
    src = result.content
    #print(src)

    soup = BeautifulSoup(src, 'html.parser')

    f = open("text.html", "w")

    title = soup.find('span', class_='article-title__text')

    f.write("{}\n{} \n\n".format("<p>this is the title:</p>", title))

    category = soup.find('div', class_='sharing-bar').
    pattern = "data-share-category=\|(.*?)\|>"
    #substring = re.search(pattern, category).group(1)
    print(category)

    #print(category)

    content = soup.find('div', class_='article-content')

    #f.write("{}{} \n\n".format("this is the whole content in 'article-content':\n", content)) #all the content of the article-content class

    #print(content)
    content = content.find_all(['p', 'h2']) #there will be more?
    #print(title)
    i = 0
    f.write("<p>this is the content text splitted into separated parts between p or h2</p>\n")
    for text in content:
        f.write("{}{}".format("-", text))
        f.write('\n')
    f.close()   


if __name__ == "__main__":
    main()