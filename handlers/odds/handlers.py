#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
from datetime import datetime, timedelta

import tornado.web

from ..misc import BaseHandler

import sys
from os.path import dirname
sys.path.append(dirname(__file__))
from tool.NowScoreProvider import NowScoreProvider

class OddsHome(BaseHandler):
    def get(self):
        self.render("odds/home.html", current_time=1000*int(time.time()))

class OddsHistory(BaseHandler):
    def get(self):
        passed = self.get_argument('passed', '1', True)
        try:
            passed = int(passed)
            if passed > 365 or passed < 1:
                passed = 1
        except (ValueError,TypeError):
            passed = 1
        date = (datetime.now() - timedelta(days=passed)).strftime('%Y/%m/%d')
        self.render("odds/previous.html", specified_date=date)

class OddsNext(BaseHandler):
    def get(self):
        page_number = self.get_argument('page_number', '1', True)
        try:
            page_number = int(page_number)
            if page_number > 7 or page_number < 1:
                page_number = 1
        except (ValueError,TypeError):
            page_number = 1
        self.render("odds/next.html", page_number=page_number, current_time=1000*int(time.time()))

class OddsDetail(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        mid = self.get_argument('mid', None, True)
        if mid is None:
            self.onResponse(None, None, None, None)
        else:
            s = self.get_argument('s', None, True)
            home = self.get_argument('home', None, True)
            guest = self.get_argument('guest', None, True)
            t = self.get_argument('t', None, True)
            rs = None
            template = None
            if s == 'a':
                rs = NowScoreProvider(mid, t).getResult()
                template = 'odds/asian_list.html'
            elif s == 'u':
                rs = NowScoreProvider(mid, t).getResult(companyFilter = ['威廉希尔','立博','Bet365','SNAI','Inter wetten',])
                template = 'odds/euro_list.html'
            self.onResponse(template, home, guest, rs)

    def onResponse(self, template, home, guest, rs):
        if template:
            odds = []
            for r in rs.odds:
                odds.append(r)
            self.render(template, oddslist=odds, home=home, guest=guest)
        else:
            self.set_status(404)
            self.finish()
