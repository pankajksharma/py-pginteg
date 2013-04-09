import os, binascii
import hashlib, base64
import urllib, urllib2
import tornado.httpserver
import tornado.ioloop
import tornado.web

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/pay", PayHandler),
            (r"/response", ResponseHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            xsrf_cookies=False,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    pass

class HomeHandler(BaseHandler):
    def get(self, error=''):
        self.render("home.html")

class PayHandler(BaseHandler):
    hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
    SALT = "3sf0jURk"
    PAYU_BASE_URL = "https://test.payu.in/_payment"

    def post(self):
        posted_params = self.request.arguments
        posted_params['txnid'] = self.get_order_id()
        print posted_params['txnid']
        hashed_val = self.get_hash(posted_params)
        # posted_params = self.sort(posted_params)
        posted_params['hash'] = hashed_val
        # data = urllib.urlencode(posted_params)
        # req = urllib2.urlopen(self.PAYU_BASE_URL, data)
        # self.write(req.read())
        self.write(hashed_val+'<br>')
        self.write(str(posted_params))
        self.render('pay.html', data=posted_params, hash=hashed_val, pg_url=self.PAYU_BASE_URL)

    def get_order_id(self):
        return binascii.b2a_hex(os.urandom(15))

    def sort(self, posted_params):
        return [(key, posted_params[key]) for key in self.hashSequence.split('|')]

    def get_hash(self, posted_params):
        hash_str = ''
        for hash_key in self.hashSequence.split('|'):
            if not posted_params.has_key(hash_key):
                posted_params[hash_key] = ['']
            hash_str += posted_params[hash_key][0]+'|'
        hash_str += self.SALT
        hash_cl = hashlib.sha512()
        hash_cl.update(hash_str)
        hashed_val = base64.b16encode(hash_cl.digest()).lower()
        return hashed_val

class ResponseHandler(BaseHandler):
    pass

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()