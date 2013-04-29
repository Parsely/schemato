from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import argparse

from schemato_web import app

args = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='The schema.to frontend web service.')
    parser.add_argument('-p', '--port', dest='PORT', type=int, nargs=1,
                   help='The port on which to listen')
    args = parser.parse_args()

    port = 5002
    try:
        port = args.PORT[0]
    except:
        pass

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port, address='0.0.0.0')
    IOLoop.instance().start()
