import scrapy
import scrapy
from datetime import datetime, timedelta, timezone
from core.spiders.upcoming import ZyteRequest, load



class ResultsSpider(scrapy.Spider):
    name = "results"
    races = ['q2 parkland', 'capalaba', 'q straight', 'q1 lakeside']
    races_dict = {
        'CPL':'capalaba',
        'QST':'ladbrokes-q-straight',
        'QLE':'ladbrokes-q1-lakeside',
        'QPD':'ladbrokes-q2-parkland',
    }


    def start_requests(self):
        self.date = datetime.now().date()
        url = f"https://api.beta.tab.com.au/v1/tab-info-service/racing/dates/{self.date}/meetings?jurisdiction=NSW&returnOffers=true&returnPromo=false"
        yield ZyteRequest(
            url=url,
            callback=self.parse_meetings,
            meta={}
        )
    
    def parse_meetings(self, response):
        resp = load(response)
        for meeting in resp['meetings']:
            if meeting['meetingName'].lower() in self.races:
                for race in meeting['races']:
                    url = f"https://api.beta.tab.com.au/v1/tab-info-service/racing/dates/{meeting['meetingDate']}/meetings/{meeting['raceType']}/{meeting['venueMnemonic']}/races/{race['raceNumber']}?returnPromo=true&returnOffers=true&jurisdiction={meeting['location']}"
                    yield ZyteRequest(
                        url=url,
                        callback=self.parse,
                        meta={'race':self.races_dict[meeting['venueMnemonic']].lower()}
                    )

    def parse(self, response):
        resp = load(response)
        if resp['parimutuelPlaceStatus'].lower() == 'closed':
            yield ZyteRequest(
                url=f"https://www.thedogs.com.au/racing/{response.meta['race']}/{self.date}?trial=false",
                callback=self.parse_all,
                meta={**response.meta , 'resp':resp}
            ) 

    def parse_all(self, response):
        dogs_rsp = load(response)
        resp = response.meta['resp']
        race_number = f"R{resp['raceNumber']}"
        distance = resp['raceDistance']
        url = dogs_rsp.xpath(f"//a[@class='race-header' and contains(.//div/text(),'{race_number}') and contains(.//div[@class='race-header__info__grade']/text(),'{distance}m')]/@href").get()
        if 'https' not in url:
            url = f"https://www.thedogs.com.au{url}"
        yield ZyteRequest(
            url=url,
            callback=self.parse_the_dogs,
            meta=response.meta
        )

    def parse_the_dogs(self, response):
        
        resp = response.meta['resp']
        dogs_resp = load(response)
        race_number = f"R{resp['raceNumber']}"
        distance = resp['raceDistance']
        for run in resp['runners']:
            dog_name = run['runnerName']
            row = dogs_resp.xpath(f'//tr[contains(translate(normalize-space(./td/div//text()), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{dog_name.lower()}")]')
            position = row.css('.race-runners__finish-position::text').get('')
            item = {
                'track_name':resp['meeting']['meetingName'],
                'date_of_race':resp['meeting']['meetingDate'],
                'race_time':resp['raceStartTime'].split('T')[1].split('.')[0],
                'box_number':run['runnerNumber'],
                'prize_money':resp['prizeMoney'],
                'whether':f"{resp['meeting']['trackCondition']} {resp['meeting']['weatherCondition']}",
                'race_number':race_number,
                'race_distance':distance,
                'dog_name':dog_name,
                'finishing_positon':position[0] if position else '',
                'fixed_odds_win':run['fixedOdds']['returnWin'],
                'fixed_odds_place':run['fixedOdds']['returnPlace'],
                'grade':resp['raceClassConditions'],
                'scraped_at': str(datetime.now())
            }
            item['dog_1st_sec'] = ''
            item['dog_2nd_sec'] = ''
            item['dog_overall_time'] = ''
            item['dog_margin'] = ''
            if row:
                try:
                    item['dog_1st_sec'] = row.css('.race-runners__sectional::text').getall()[0]
                    item['dog_2nd_sec'] = row.css('.race-runners__sectional::text').getall()[1]
                    item['dog_overall_time'] = row.css('.race-runners__time::text').get()
                    item['dog_margin'] = row.css('.race-runners__margin::text').get()
                except:
                    pass
            yield item
