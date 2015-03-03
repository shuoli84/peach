from flask import Flask, request, send_from_directory, Response
import requests
import hashlib
import os
import json
from collections import namedtuple
import argparse
import sys

parser = argparse.ArgumentParser(description='Peach, file download cache server')
parser.add_argument('--host', default="0.0.0.0", help='Interface the peach server will listen on')
parser.add_argument('--port', '-p', default=5000, help='port of the peach server')
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

FileNode = namedtuple('FileNode', ['url', 'hash', 'cache_file_path', 'header_file_path', 'data_file_path', 'succeed_flag_path'])

def get_file_node(url):
    m = hashlib.md5()
    m.update(url)
    hash_code = m.hexdigest()
    cache_file_path = os.path.join(cache_folder, hash_code)
    header_file_path = os.path.join(cache_file_path, 'headers.json')
    data_file_path = os.path.join(cache_file_path, 'data')
    succeed_flag_path = os.path.join(cache_file_path, 'succeed')
    return FileNode(url=url, hash=hash_code, cache_file_path=cache_file_path, header_file_path=header_file_path, data_file_path=data_file_path, succeed_flag_path=succeed_flag_path)

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

@app.route('/', methods=['GET'])
def index():
    file_url = request.args.get('file_url').strip()

    if file_url is None:
        return Response(status=400)

    file_node = get_file_node(file_url)
    cache_file_path = file_node.cache_file_path
    header_file_path = file_node.header_file_path
    data_file_path = file_node.data_file_path

    if os.path.exists(cache_file_path):
        if os.path.exists(header_file_path) and os.path.exists(data_file_path):
            with open(header_file_path, 'r') as f:
                headers = json.load(f)
                headers.pop('transfer-encoding', None)
                if 'content-length' in headers:
                    length = int(headers['content-length'])
                    file_length = os.path.getsize(data_file_path)
                    if length < file_length:
                        pass

            def stream_file(file_path):
                current_offset = 0

                with open(file_path, 'rb') as f:
                    chunk = f.read(50 * 1024)
                    while len(chunk):
                        yield chunk
                        chunk = f.read(50 * 1024)
            return Response(stream_file(data_file_path), headers=headers)


    if not os.path.exists(cache_file_path):
        os.mkdir(cache_file_path)

    res = requests.get(file_node.url, stream=True, proxies=proxies)
    res.raise_for_status()

    headers = dict(res.headers)
    with open(header_file_path, 'w') as f:
        json.dump(headers, f)

    headers.pop('transfer-encoding', None)

    def download_file():
        current_offset = 0

        chunk = res.raw.read(1024 * 1024)
        while len(chunk) > 0:
            with open(data_file_path, 'wb') as f:
                f.seek(current_offset)
                f.write(chunk)
                f.flush()
                current_offset += len(chunk)
                yield chunk
            chunk = res.raw.read(1024 * 1024)
        touch(file_node.succeed_flag_path)

    return Response(download_file(), headers=headers)


if __name__ == '__main__':
    app.run(args.host, port=args.port, debug=args.debug)


