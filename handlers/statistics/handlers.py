import time
from datetime import datetime, timedelta

import tornado.web

from handlers.misc import DBHandler
from handlers.misc import BaseHandler

import sys
from os.path import dirname
sys.path.append(dirname(__file__))

from handlers.statistics.tool.WhoScoredProvider import WhoScoredProvider

class StatisticsHome(BaseHandler):
    def get(self):
        self.render("statistics/home.html")

class StatisticsList(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        url = self.get_argument('url', None, True)
        name = self.get_argument('name', '', True)
        if url:
            matches, id_match = WhoScoredProvider(None).GetMatchesLink(leagueURL=url)
            self.onResponse(name, matches)
        else:
            self.onResponse(None, None)

    def onResponse(self, league, matches):
        if matches:
            self.render('statistics/leagues_matches.html', league=league, matches=matches)
        else:
            self.set_status(404)
            self.finish()

class StatisticsDetail(DBHandler):
    @tornado.web.asynchronous
    def get(self):
        home_id = self.get_argument('home_id', 0, True)
        home_name = self.get_argument('home_name', '', True)
        home = (home_id, home_name)

        guest_id = self.get_argument('guest_id', 0, True)
        guest_name = self.get_argument('guest_name', '', True)
        guest = (guest_id, guest_name)

        if home_id is 0 or guest_id is 0:
            self.onResponse(None, None, None)
        else:
            statistics = WhoScoredProvider(self.db).GetClubStatics(home_id, guest_id)
            self.onResponse(home, guest, statistics)

    def onResponse(self, home, guest, statistics):
        if statistics:
            self.render('statistics/against_stat.html', home=home[0], away=guest[0], homeJS=statistics[0][1], awayJS=statistics[1][1])
        else:
            self.set_status(404)
            self.finish()
