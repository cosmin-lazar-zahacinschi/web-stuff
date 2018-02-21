'''
Created on Feb 21, 2018

@author: czahacinschi
'''
from HTMLParser import HTMLParser

class CustomHTMLParser(HTMLParser, object):
        
    def __init__(self):
        super(CustomHTMLParser, self).__init__()
        self.urlList = []
        
    def handle_starttag(self, tag, attrs):
        if (tag == 'a'):
            for name, value in attrs:
                if (name == 'href'):
                    self.urlList.append(value)
                
    def get_url_list(self, text):
        self.feed(text)
        return self.urlList