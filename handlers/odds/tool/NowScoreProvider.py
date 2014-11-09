# -*- coding: UTF8 -*-
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from tool.MatchOdds import MatchOdds, Odds
from handlers.misc import HtmlCache

cache = HtmlCache('/temp/nowscore/')
allCompanies = [
        (1, "澳门"),
        (12, "易胜博"),
        (8, "Bet365"),
        (22, "10Bet"),
        (3, "SB"),
        (4, "立博"),
        (14, "韦德"),
        (17, "明陞"),
        (23, "金宝博"),
        (24, "沙巴"),
        (31, "利记"),
        (9, "威廉希尔"),
        (7, "SNAI"),
        (18, "EuroBet"),
        (19, "Inter wetten"),
        (35, "盈禾")
]

class NowScoreProvider():
    def __init__(self, mid, t):
        self.mid = mid
        delta = 7 * 24 * 60 * 60
        if t:
            minutes = int(t.split(':')[0]) * 60 + int(t.split(':')[1])
            now = datetime.now()
            delta = minutes - now.hour * 60 - now.minute
            if delta <= 30:
                m = 5 * 60;
            elif delta <= 60:
                m = 10 * 60;
            elif delta < 120:
                m = 15 * 60;
            else:
                delta = 30 * 60;
        else:
            delta = 7 * 24 * 60 * 60;
        self.timeout = delta

    def __getOddsByCompanyId(self, cid):
        url = 'http://live1.nowscore.com/odds/3in1Odds.aspx?companyid={1}&id={0}'.format(self.mid, cid)
        return cache.getContent(url, timeout=self.timeout)

    def getResult(self, companyFilter = []):
        caredCompanies = []
        if companyFilter:
            for company in companyFilter:
                for item in allCompanies:
                    if item[1] == company:
                        caredCompanies.append(item)
        else:
            caredCompanies = [a for a in allCompanies[0:10]]
        matchOdds = MatchOdds()
        for c in caredCompanies:
            html, cached = self.__getOddsByCompanyId(c[0])
            soup = BeautifulSoup(html)
            tables = soup.findAll('table', {"class":'gts', "bgcolor":"#DDDDDD"})
            o = Odds()
            o.company = c[1]
            # 亚盘
            for tr in tables[0].findAll('tr')[1:]:
                tds = tr.findAll('td')
                if len(tds) < 7 or tds[6].get_text().strip() == '滚':
                    continue
                t = tds[5].get_text().strip()
                t = '{0} {1}'.format(t[0:5], t[5:])
                s1 = tds[2].get_text().strip()
                p = tds[3].get_text().strip()
                s2 = tds[4].get_text().strip()
                o.asian.append((t, s1, p, s2))

            # 大小盘
            for tr in tables[1].findAll('tr')[1:]:
                tds = tr.findAll('td')
                if len(tds) < 7 or tds[6].get_text().strip() == '滚':
                    continue
                t = tds[5].get_text().strip()
                t = '{0} {1}'.format(t[0:5], t[5:])
                s1 = tds[2].get_text().strip()
                p = tds[3].get_text().strip()
                s2 = tds[4].get_text().strip()
                o.over.append((t, s1, p, s2))

            # 欧赔
            for tr in tables[2].findAll('tr')[1:]:
                tds = tr.findAll('td')
                if len(tds) < 7 or tds[6].get_text().strip() == '滚':
                    continue
                t = tds[5].get_text().strip()
                # 变化时间
                t = '{0} {1}'.format(t[0:5], t[5:])
                # 主队赔率
                s1 = tds[2].get_text().strip()
                # 平局赔率
                s2 = tds[3].get_text().strip()
                # 客队赔率
                s3 = tds[4].get_text().strip()
                # 返还率
                p = ('%.2f' % (100.0 * float(s1)*float(s2)*float(s3)/(float(s2)*float(s3)+float(s1)*float(s3)+float(s1)*float(s2))))
                o.euro.append((t, s1, s2, s3, p))
            matchOdds.odds.append(o)
        return matchOdds;

if __name__ == "__main__":
    o = NowScoreProvider('853476')
    rs = o.getResult()

    for r in rs.odds:
        print(r.company)
        for a in r.asian:
            print(a)

        for a in r.euro:
            print(a)
