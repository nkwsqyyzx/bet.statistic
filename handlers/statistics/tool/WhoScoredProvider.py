# -*- coding: UTF8 -*-
import time
import logging

from datetime import datetime, timedelta

from handlers.misc import HtmlCache

LOG = logging.getLogger(__name__)

class WhoScoredProvider():
    global cache
    cache = HtmlCache('/temp/whoscored/')
    timeout = 365 * 24 * 60 * 60

    def __init__(self, connection):
        self.connection = connection

    def GetMatchesLink(self, leagueURL='Regions/252/Tournaments/7/England-Championship'):
        # 从每个联赛中获取下一轮比赛对阵链接
        url = 'http://www.whoscored.com/{0}'.format(leagueURL)
        html, cached = cache.getContentWithAgent(url=url, encoding='gbk', timeout=24*60*60)
        js = html.split('calendar.parameter()), ')[1].split(']);')[0].replace('\r\n', '')
        js = 'var matches = {0}];'.format(js)

        aa = 'var id_match = [[{0}];'.format(']')
        return js, aa

    def __ensureClubRecord(self, clubId, clubName):
        if not self.connection.query('select id from t_team where id={0}'.format(clubId)):
            self.connection.execute('insert into t_team values({0},"{1}");'.format(clubId, clubName))
            self.connection.execute('create table if not exists t_team_match_{0}(id INTEGER PRIMARY KEY, time INTEGER)'.format(clubId))

    def __safeInsertMatchRecord(self, clubId, matchId, time):
        if not self.connection.query('select id from t_team_match_{0} where id={1}'.format(clubId, matchId)):
            self.connection.execute('insert into t_team_match_{0} values({1}, {2});'.format(clubId, matchId, time))

    def __getMatchesByClub(self, clubId=15):
        # 从球队链接中获取其所有比赛号
        # => list of (matchid, home, away)
        link = 'http://www.whoscored.com/Teams/{0}/Fixtures/'.format(clubId)
        html, cached = cache.getContentWithAgent(url=link, encoding='gbk', timeout=3*24*60*60)
        conn = self.connection
        try:
            hs = html.split('parametersCopy), ')
            js = hs[1].split('var teamFixtures ')[0].replace('\r\n', '')[0:-2]
            js = js.replace(',,',', None,')
            allMatches = eval(js)
            if allMatches:
                j = allMatches[0]
                self.__ensureClubRecord(j[4], j[5])
                self.__ensureClubRecord(j[7], j[8])
            for j in allMatches:
                # 根据who_scored网站的规则判断是否有赛后报告
                if j[1] == 1 and (j[26] == 1 or j[27] == 1) and (not self.__matchHasTerminatedUnexpectedly(j[14])):
                    pass
                else:
                    continue
                m = j
                # 保存对阵信息
                match_id = m[0]
                home_id = m[4]
                guest_id = m[7]
                t = m[2] + " " + m[3]
                t = time.strptime(t, '%d-%m-%Y %H:%M')
                t = int(time.mktime(time.localtime(time.mktime(t) + 8 * 60 * 60)))
                self.__safeInsertMatchRecord(home_id, match_id, t)
                self.__safeInsertMatchRecord(guest_id, match_id, t)
        except Exception as e:
            print("__getMatchesByClub", clubId, e)

    def __matchHasTerminatedUnexpectedly(self, status):
        return status == 'Abd' or status == "Post" or status == "Can" or status == "Susp"

    def __tr(self, s):
        i1 = 0
        i2 = 1
        r = s
        while True:
            i1 = r.find('"', i1)
            i2 = r.find('"', i1 + 1)
            if i1 < 0 or i2 < 0:
                break;
            s1 = r[0:i1]
            s2 = r[i1:i2+1]
            s2 = s2.replace("'", '-')
            s2 = s2.replace('"', "'")
            s3 = r[i2+1:]
            r = s1 + s2 + s3
            i1 = i2 + 2
        return r

    def __safeInsertMatchDetail(self, matchId, detail):
        if not self.connection.query('select id from t_match where id={0}'.format(matchId)):
            sql = 'insert into t_match values({0}, "{1}");'.format(matchId, detail)
            self.connection.execute(sql)

    def __fetchOriginalData(self, matchid='758062'):
        url = 'http://www.whoscored.com/Matches/{0}/MatchReport'.format(matchid)
        html, cached = cache.getContentWithAgent(url=url, encoding='gbk', timeout=30*24*60*60)
        d = None
        try:
            if 'var matchStats = ' in html:
                d = html.split('var matchStats = ')[1]
                d = d.split('var liveTeamStatsInfoConfig =')[0]
                d = d.replace('\r', '')
                d = d.replace('\n', '')
                d = d.replace(';', '')
                i = d.find(']')
                m = d[3:i].split(',')
                match_id = matchid
                home_id = m[0]
                home_name = m[2]
                guest_id = m[1]
                guest_name = m[3]
                self.__safeInsertMatchDetail(match_id, self.__tr(d))
        except Exception as e:
            print(match_id, e)

        return eval(d)

    def __queryStatistics(self, clubId):
        if not self.connection.query('show tables like "t_team_match_{0}"'.format(clubId)):
            return []
        sql = 'select t.id as id, tm.statistics as statistics from (select id from t_team_match_{0} order by time desc limit 15) t left join t_match tm on tm.id = t.id'
        return [[t.id, t.statistics] for t in self.connection.query(sql.format(clubId))]

    def GetClubStatics(self, home_id, guest_id):
        self.__getMatchesByClub(home_id)
        self.__getMatchesByClub(guest_id)
        homeData = self.__queryStatistics(home_id)
        for t in homeData:
            if not t[1]:
                t[1] = self.__fetchOriginalData(t[0])
        awayData = self.__queryStatistics(guest_id)
        for t in awayData:
            if not t[1]:
                t[1] = self.__fetchOriginalData(t[0])
        return [str(homeData), str(awayData)]
