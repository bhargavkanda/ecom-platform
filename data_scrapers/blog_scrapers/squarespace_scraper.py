import httplib
import json
import pdb
import time
import urllib2

from bs4 import BeautifulSoup, Comment

link_prefix = r'http://blog.zapyle.com'

def get_blog_metaData():
    with open(r'/home/sg/Zapcodebase/zapyle_new/data_scrapers/blog_scrapers/squarespace_dump.json', 'r') as f:
        dump = json.load(f)
    items = dump['rss']['channel']['item']
    posts = [{'id': int(item['post_id']['__text']), 'title': item['title'], 'link': item['link'], 'status': item['status']['__text'],
              'date': item['post_date']['__text'], 'scraped': False} for item in items
             if item['post_type']['__text'] == 'post' and item['status']['__text'] == 'publish']

    for i in range(0,len(posts)):
        posts[i]['id'] = i

    with open(r'/home/sg/Zapcodebase/zapyle_new/data_scrapers/blog_scrapers/scraped_data.json', 'w') as f:
        write_obj = {'posts': posts}
        json.dump(write_obj, f)

    return posts


def process_encoded_data():
    posts = get_blog_metaData()

    for post in posts:
        content = post['content']
        soup = BeautifulSoup(content, 'lxml')
        body = soup.findAll('div', {'id': 'content'})
        post['content'] = body

    return posts


def scrape_blogs():
    # pdb.set_trace()
    with open(r'/home/sg/Zapcodebase/zapyle_new/data_scrapers/blog_scrapers/scraped_data.json', 'r+') as f:
        posts = json.load(f)['posts']

    for post in posts:
        if not post['scraped']:
            html = get_page(post)
            soup = BeautifulSoup(html, 'lxml')
            content = soup.find('div', {'id': 'content'})
            comments = content.findAll(text=lambda text: isinstance(text, Comment))
            map(lambda x: x.extract(), comments)
            post['content'] = content.prettify()
            print post

    print posts

    with open(r'/home/sg/Zapcodebase/zapyle_new/data_scrapers/blog_scrapers/scraped_data.json', 'w+') as f:
        json.dump({'posts': posts}, f)

    return posts


def get_page(post):
    try:
        link = ''.join([link_prefix, post['link']])
        print '[{}] Hit url : {}'.format(post['id'], link)
        request = urllib2.Request(link)
        response = urllib2.urlopen(request)
        html = response.read()
        print '\t-------------> Received response status {} {} \n'.format(response.code, response.msg)
        post['scraped'] = True
        time.sleep(40)
        return html
    except urllib2.HTTPError as e:
        print '\t-------------> Received response status {} {} \n'.format(e.code, e.msg)
        return ''
    except:
        print 'Unknown Exception Caught!'
        return ''


