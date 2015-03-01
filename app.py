from flask import Flask, request, send_from_directory, Response
import requests
import hashlib
import os
import json

app = Flask(__name__)

proxies = None
cache_folder = '/peach/cache'

if not os.path.exists(cache_folder):
    os.mkdir(cache_folder)


@app.route('/', methods=['GET'])
def index():
    file_url = request.args.get('file_url').strip()

    if file_url is not None:
        m = hashlib.md5()
        m.update(file_url)
        hash_code = m.hexdigest()
        cache_file_path = os.path.join(cache_folder, hash_code)
        header_file_path = os.path.join(cache_file_path, 'headers.json')
        data_file_path = os.path.join(cache_file_path, 'data')

        if os.path.exists(cache_file_path):
            if os.path.exists(header_file_path) and os.path.exists(data_file_path):
                with open(header_file_path, 'r') as f:
                    headers = json.load(f)
                    return send_from_directory(cache_file_path, 'data', mimetype=headers['content-type'])

        if not os.path.exists(cache_file_path):
            os.mkdir(cache_file_path)

        res = requests.get(file_url, stream=True, proxies=proxies)
        headers = dict(res.headers)
        with open(header_file_path, 'w') as f:
            json.dump(headers, f)

        def download_file():
            with open(data_file_path, 'w') as f:
                for chunk in res.iter_content(chunk_size=1024*50):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        yield chunk
        return Response(download_file(), headers={
            'last-modified': headers.get('last-modified', None),
            'etag': headers.get('etag', None),
            'content-type': headers.get('content-type'),
            })


if __name__ == '__main__':
    app.run('0.0.0.0')
