import os
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
    SECURE_SECRET = 'c93ca2497afa7d5365f5ffe0546a3945'

class HomeHandler(BaseHandler):
    def get(self):
        self.render("index.html")

class PayHandler(BaseHandler):
    keys_to_be_ignored = ["virtualPaymentClientURL", "SubButL", "secret", "_xsrf", "submitted"]
    
    def post(self):
        # user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        # cookie = '__utma=111872281.788926790.1364020825.1365229884.1365234158.13; __utmz=111872281.1364020825.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); verification="Yzc4MDliMDU5OWVmZWExZTI0NmY5ZjU5MGIzN2JlZWY2YThkMTU4MjNiNTk1NzQyMDFjMjMzYWM5YzVmOWRmZg==|1364926450|1413b3e04eeaa1de71429c23aa72add9e9ec0dc5"; session_id="MTlhZGFhNWNmZjdjNDZiMjI4NWQxYWM4ZjY2ZDdjYjRkZDlmZTg2Y2RhNDY5NTc0MDc3NDFiYTE2NDE2M2QwMA==|1364926450|345ae52e2776d75423872a126ea1f23f32ec0a85"; __utmb=111872281.3.10.1365234158; _xsrf=473d9e0e6f4643938f138f824645a5de; httponly; merchant="NA==|1365227310|26f1e87d478a5f13b84f5bd75a2ee1fda33c9aac"; __utmc=111872281'
        # header = { 'User-Agent' : user_agent, 'Cookie' : cookie }
        # cookies = {}
        # for c in cookie.split(';'):
        #     print c
        #     #cookies[c.split('=')[0]] = c.split('=')[1]
        # print cookie
        pg_url = self.get_argument("virtualPaymentClientURL", None)
        md5_hash, variables = self.get_md5_hash()
        # print md5_hash, variables
        post_data = {}
        for (key, value) in variables:
            if key not in self.keys_to_be_ignored and len(value[0])>0:
                post_data[key] = str(value[0])
        post_data['vpc_SecureHash'] = md5_hash
        #print pg_url, post_data
        # post_data =  urllib.urlencode(post_data)
        # request = urllib2.Request(pg_url, headers=header, data=post_data)
        # resp = urllib2.urlopen(request)
        # self.write(str(resp.read()))
        self.render("pay.html", pg_url=pg_url,post_data=variables, md5_hash=md5_hash)
        

    def ksort(self, dic):
        return [(k, dic[k]) for k in sorted(dic.keys())]

    def get_md5_hash(self):
        md5_cl = hashlib.md5()
        md5_hash_data = self.SECURE_SECRET
        variables = self.ksort(self.request.arguments)
        ret_variables = []
        for (key, value) in variables:
            if key not in self.keys_to_be_ignored and len(value[0])>0:
                print key, value[0]
                md5_hash_data += '|' + str(value[0])
                ret_variables.append((key, value))
        print md5_hash_data
        md5_cl.update(md5_hash_data)
        return base64.b16encode(md5_cl.digest()).upper(), ret_variables

class ResponseHandler(BaseHandler):
    def post(self):
        for (key, value) in self.request.arguments.iteritems():
            self.write(key+' is '+value[0]+'<br>')

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()