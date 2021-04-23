class ScraperInterface:

    def __init__(self):
        pass

    def getArticleList(self):
        list = ["Test", "Hallo", "Tada", "Wie", "Geht's"]
        return list

    def downloadArticles(self, list):
        for article in list:
            print(article)
