'''
Created on Feb 20, 2018

@author: czahacinschi
'''
from urlparse import urlsplit
import urllib
import urlparse
from urllib2 import Request, urlopen, HTTPError, URLError
import time
from contextlib import contextmanager
from com.test.CustomHTMLParser import CustomHTMLParser
from httplib import BadStatusLine

@contextmanager
def timeit_context(name):
    startTime = time.clock()
    yield
    elapsedTime = time.clock() - startTime
#     print('[{}] finished in {} ms'.format(name, elapsedTime * 100))

def url_fix(s, charset='utf-8'):
    """Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    :param charset: The target charset for the URL if the url was
                    given as unicode string.
    """
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def parse_node(url, urlList):
    print("Opening " + url)
    req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
    
    with timeit_context("url open"):
        try:
            page = urlopen(req)
        except HTTPError as e:
            print(e)
            return
        except BadStatusLine as e:
            print(e)
            return
        except URLError as e:
            print(e)
            return
    
    content_type = page.headers['Content-Type']
    
    if not 'text/html' in content_type:
        return
    
    charset = 'utf-8'
    
    for type_ in content_type.split(';'):
        if (type_.find('charset') != -1):
            charset = type_[8:]
    
    with timeit_context("url read"):
        html_string = page.read()
            
    with timeit_context("html parsing"):
#         root = lxml.html.fromstring(html_string)
#         urls = root.xpath('//a/@href')
        try:
            parser = CustomHTMLParser()
            urls = parser.get_url_list(unicode(html_string, charset.lower()))
        except UnicodeDecodeError as e:
            print(e)
            return
        
    base_split = urlsplit(url)
    
    with timeit_context("process urls"):
        for url in urls:
            split_url = urlsplit(url)
            
            if (split_url != '' and split_url.scheme != 'http' and 
                split_url.scheme != 'https'):
                continue
            
            final_url = ''
            
            if (split_url.scheme != ''):
                final_url += split_url.scheme
            else:
                final_url += base_split.scheme
            final_url += '://'
            
            if (split_url.netloc != ''):
                final_url += split_url.netloc
            else:
                final_url += base_split.netloc
            
            path = ''
            if (split_url.path != ''):
                path += split_url.path
            elif (base_split.path != ''):
                path += base_split.path
            if (path != ''):
                final_url += path
            else:
                urlList.append(url_fix(final_url))
                continue
            
            query = ''
            if (split_url.query != ''):
                query = split_url.query
            elif (base_split.query != ''):
                query = base_split.query
            if (query != ''):
                final_url += '?' + query
            urlList.append(url_fix(final_url))   

def parse_root(root):
    
    nodeFifo = []
    nodeFifo.append(root)
    
    while (len(nodeFifo) > 0):
        node = nodeFifo.pop(0)
        
        with timeit_context("process node"):
            parse_node(node, nodeFifo);

if __name__ == '__main__':
       
    root = 'http://www.hotnews.ro'
    parse_root(root)