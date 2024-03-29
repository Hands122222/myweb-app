#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Hands'
__emial__='handssky@foxmail.com'

'''
async web application.
'''

import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
    return web.Response(body=b'<h1>Hands\' First Page</h1>',content_type='text/html')

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), 'localhost', 8080)
    logging.info('server started at http://localhost:8080...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()