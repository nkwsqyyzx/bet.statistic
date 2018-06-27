import hashlib
import os.path
import time

import requests
import tornado.web


class Application(tornado.web.Application):
    def __init__(self, handlers, settings, options):
        host = options.host
        user = options.user
        password = options.password
        database = options.database
        tornado.web.Application.__init__(self, handlers, **settings)


class HtmlCache:
    def __init__(self, basepath):
        self.basepath = basepath

    def getCachedHtml(self, url, encoding, timeout):
        m = hashlib.md5()
        m.update(url.encode())
        md5value = m.hexdigest()
        html = None
        fpath = '{0}{1}.html'.format(self.basepath, md5value)
        if os.path.exists(fpath):
            outofdate = time.time() - os.path.getmtime(fpath) > timeout
            if outofdate:
                return html, fpath
            with open(fpath, 'r', encoding=encoding) as f:
                try:
                    html = ''.join(f.readlines())
                except UnicodeDecodeError:
                    pass
        return html, fpath

    def getContent(self, url, encoding='utf-8', cache=1, timeout=30 * 60):
        if cache:
            html, fpath = self.getCachedHtml(url, encoding, timeout)
            if html:
                return html, True
            else:
                html = requests.get(url).decode(encoding, errors='ignore')
                if not os.path.exists(self.basepath):
                    os.makedirs(self.basepath)
                with open(fpath, 'w', encoding=encoding) as outfile:
                    outfile.write(html)
                return html, False
        else:
            html = requests.get(url).decode(encoding)
            return html, False

    def getContentWithAgent(self, url, encoding='utf-8', cache=1, timeout=30 * 60,
                            userAgent='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)'):
        if cache:
            html, fpath = self.getCachedHtml(url, encoding, timeout)

            if html:
                return html, True
        session = requests.Session()
        request = requests.Request(url=url, headers={'User-Agent': userAgent})
        try:
            r = request.prepare()
            r = session.send(r)
            html = r.content.decode(encoding, errors='ignore')
            if not os.path.exists(self.basepath):
                os.makedirs(self.basepath)
            with open(fpath, 'w', encoding=encoding) as outfile:
                outfile.write(html)
        except Exception as e:
            print(url, e)
        return '', False


class BaseHandler(tornado.web.RequestHandler):
    pass


class DBHandler(BaseHandler):
    @property
    def db(self):
        return self.application.db


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("home.html")
