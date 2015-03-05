from flask import Flask, request, send_from_directory, Response
import requests
import hashlib
import os
import json
from collections import namedtuple
import argparse
import sys
import urlparse

parser = argparse.ArgumentParser(description='Peach, file download cache server')
parser.add_argument('--host', default="0.0.0.0", help='Interface the peach server will listen on')
parser.add_argument('--port', '-p', default=5000, type=int, help='port of the peach server')
parser.add_argument('--cache', '-c', default='/var/opt/peach/cache/', help='Path where peach cache downloaded files, default /peach/cache')
parser.add_argument('--http_proxy', default=None, help='http proxy')
parser.add_argument('--https_proxy', default=None, help='https proxy')
parser.add_argument('--debug', action="store_true", help='Debug mode')

args = parser.parse_args()

app = Flask(__name__)

proxies = {
    'http_proxy': args.http_proxy,
    'https_proxy': args.https_proxy
}

cache_folder = args.cache

if not os.path.exists(cache_folder):
    print "Path not exists, please create it first:", cache_folder
    sys.exit(1)

FileNode = namedtuple('FileNode', ['url', 'hash', 'file_name', 'cache_file_path', 'header_file_path', 'data_file_path', 'succeed_flag_path'])

def get_file_node(url):
    m = hashlib.md5()
    m.update(url)
    hash_code = m.hexdigest()
    cache_file_path = os.path.join(cache_folder, hash_code)
    header_file_path = os.path.join(cache_file_path, 'headers.json')
    data_file_path = os.path.join(cache_file_path, 'data')
    path = urlparse.urlsplit(url).path
    file_name = urlparse.urlsplit(url).path.split('/')[-1] or 'index.html'

    for path in [cache_file_path, data_file_path]:
        if not os.path.exists(path):
            os.mkdir(path)

    succeed_flag_path = os.path.join(cache_file_path, 'succeed')
    return FileNode(url=url, hash=hash_code, file_name=file_name, cache_file_path=cache_file_path, header_file_path=header_file_path, data_file_path=data_file_path, succeed_flag_path=succeed_flag_path)

def get_downloaded_size(path):
    current_offset = 0
    while os.path.exists(os.path.join(path, str(current_offset))):
        current_offset += os.path.getsize(os.path.join(path, str(current_offset)))
    return current_offset

def stream_folder(file_path):
    current_offset = 0

    while os.path.exists(os.path.join(file_path, str(current_offset))):
        with open(os.path.join(file_path, str(current_offset)), 'rb') as f:
            app.logger.debug("streaming %s" % os.path.join(file_path, str(current_offset)))
            chunk = f.read(1024 * 1024)
            while len(chunk):
                current_offset += len(chunk)
                yield chunk
                chunk = f.read(1024 * 1024)

def stream_folder_then_socket(file_path, socket):
    current_offset = 0

    app.logger.info("streaming folder[%s] and socket[%s]" % (file_path, socket))
    for chunk in stream_folder(file_path):
        current_offset += len(chunk)
        yield chunk

    if socket is not None:
        chunk = socket.read(50 * 1024)
        with open(os.path.join(file_path, str(current_offset)), 'wb') as f:
            app.logger.debug("writing socket data to %s", os.path.join(file_path, str(current_offset)))
            while len(chunk) > 0:
                f.write(chunk)
                f.flush()
                current_offset += len(chunk)
                yield chunk
                chunk = socket.read(50 * 1024)

    app.logger.info("streaming folder[%s] and socket[%s] finished" % (file_path, socket))

@app.route('/', methods=['GET'])
def index():
    file_url = request.args.get('file_url').strip()

    if file_url is None:
        return Response(status=400)

    file_node = get_file_node(file_url)
    res = None # response object when we need download data from network, None if the file is 100% cached

    if os.path.exists(file_node.header_file_path) and os.path.exists(file_node.data_file_path):
        app.logger.info("Url file node existing")

        headers = {}
        with open(file_node.header_file_path, 'r') as f:
            headers = json.load(f)

        file_length = get_downloaded_size(file_node.data_file_path)
        if int(headers.get('content-length', '0')) > file_length:
            length = int(headers['content-length'])
            app.logger.info("Partial file, download rest part")
            if headers.get('accept-ranges', None) != 'bytes':
                app.logger.info("Server not supporting range, we have to redownload everything")
                res = requests.get(file_node.url, stream=True, proxies=proxies)
            else:
                app.logger.debug("Server support range")
                res = requests.get(file_node.url, stream=True, proxies=proxies, headers={
                    "range": "bytes=%d-" % file_length
                    })
        else:
            app.logger.info("The whole file is cached, we should just stream it out")
    else:
        app.logger.debug("Fresh url, download it")
        res = requests.get(file_node.url, stream=True, proxies=proxies)

        headers = dict(res.headers)
        headers['peach-transfer-encoding'] = headers.pop('transfer-encoding', None)

        with open(file_node.header_file_path, 'w') as f:
            json.dump(headers, f)

    if res is not None:
        if res.status_code >= 400:
            return Response(status=res.status_code)

    socket = res.raw if res is not None else None

    if 'content-disposition' not in headers:
        headers['content-disposition'] = "inline; filename=\"%s\"" % file_node.file_name
    return Response(stream_folder_then_socket(file_node.data_file_path, socket), headers=headers)

if __name__ == '__main__':
    app.run(args.host, port=args.port, debug=args.debug)
