from ftw.testbrowser import browser


class Event(object):

    def __init__(self, node):
        self.node = node

    @property
    def title(self):
        return self.node.css('.title').first.text

    @property
    def url(self):
        link = self.node.css('.title a')
        if link:
            return link.first.attrib['href']
        else:
            return None

    @property
    def byline(self):
        return self.node.css('.byline').first.text

    def infos(self):
        return {'title': self.title,
                'url': self.url,
                'byline': self.byline}


def events(browser=browser):
    return map(Event, browser.css('.activity .events .event'))


def events_infos(browser=browser):
    return [event.infos() for event in events(browser)]
