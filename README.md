PEACH - lightweight file download cache
===

Motivation
---
I am tired of waiting for file downloading again and again while learning and trying chef, vagrant etc. It is even worse when you living in a country with slow internet connection :).

How it works
---
Very simple, we can't cache files as a proxy, then we have to do it on client. Peach contains two sides, server & client. The server side provides an endpoint any client can use it to download files. The client side are some scripts which overrides default wget, curl etc, to make them peach aware.

Server
---
The server can download and cache files, it provides a minimalist api: http://host:port/download?url=url. Then the file will be cached on disk, all future download can be streamed directly.

Client
---
A thin wrapper on wget, which aware the Peach server and can download from it directly.

Installation
---
TBD

Contribution
---
Any pull request is welcomed

RoadMap
---
wget
Curl wrapper
Basic auth
Other means to download files, e.g, btsync
