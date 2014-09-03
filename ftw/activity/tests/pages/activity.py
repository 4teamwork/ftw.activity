from ftw.testbrowser import browser


class Event(object):

    def __init__(self, node):
        self.node = node

    @property
    def title(self):
        return self.node.css('.title').first.text

    @property
    def url(self):
        return self.node.css('.title a').first.attrib['href']

    @property
    def byline(self):
        return self.node.css('.byline').first.text


def events(browser=browser):
    return map(Event, browser.css('.activity .events .event'))
