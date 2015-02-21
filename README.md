PEACH - lightweight file download cache
===

Motivation
---
I am tired of waiting for file downloading again and again while learning and trying chef, vagrant etc. It is even worse when you living in a country with slow internet connection :).

How it works
---
Very simple, we can't cache files as a proxy, then we have to do it on client. Peach contains two sides, server & client. The server side provides an endpoint any client can use it to download files. The client side are some scripts which overrides default wget, curl etc, to make them peach aware.

####Server
The server can download and cache files, it provides a minimalist api: http://host:port/download?url=url. Then the file will be cached on disk, all future download can be streamed directly. 

####Client
A thin wrapper on wget, which aware the Peach server and can download from it directly. When the Env PEACH_SERVER setted, the wrapper will replace url to http://peach_server?file_url=<original_url>, all other params will be passed through to underlying command without any change.

After the installation, wget is super charged:
```sh
vagrant@vagrant-ubuntu-trusty-64:~$ wget https://opscode-omnibus-packages.s3.amazonaws.com/ubuntu/13.04/x86_64/chef_12.0.3-1_amd64.deb
...
100%[============================================================================================>] 43,799,970  17.4MB/s   in 2.4s
...
```

Installation
---
###Server

#####Vagrant
```sh
vagrant up
```

#####Start from code
```sh
git clone the project
pip install -r requirements.txt
python app.py
```

###Client
Grab the tools folder in the same folder with Vagrantfile, then add following to Vagrantfile shell provision

```sh
mkdir -p /etc/peach
echo {\\"server\\": \\"10.0.2.2:5000\\"} > /etc/peach/conf.json
echo "export PATH=/vagrant/tools:$PATH" > /etc/profile.d/peach.sh
```

Contribution
---
Any pull request is welcomed. Or just star the project.

RoadMap
---
1. wget
2. Curl
3. vagrant, chef etc framework support
4. Basic auth
5. Server side, other means to download files, e.g, btsync
