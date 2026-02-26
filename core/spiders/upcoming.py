import scrapy
import scrapy
import os
import base64
import json
from scrapy import Request, Selector
from datetime import datetime, timedelta, timezone

def get_date_list():
    now = datetime.now()

    start_date = now.date()  
    end_date = (now + timedelta(hours=72)).date()   # date after 72h

    dates = []
    current = start_date

    while current <= end_date:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates

class ZyteRequest(Request):
    def __init__(self, url, meta={}, *args, **kwargs):
        api_key = os.getenv("ZYTE")
        if not api_key:
            raise ValueError("ZYTE_API environment variable not set")
        self._url = url
        self._meta = meta
        # Prepare auth header
        auth_str = f"{api_key}:".encode()
        auth_header = base64.b64encode(auth_str).decode()

        # Headers and JSON payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}",
        }

        payload = {
            "url": url,
            "httpResponseBody": True,
            "geolocation":"AU",
            #"browserHtml":True,
            #"httpRequestMethod": kwargs.get("method", "GET"),
        }
        if cookies := kwargs.get("cookies"):
            payload["requestCookies"] = cookies
        custom_headers = kwargs.pop("headers", None)
        if custom_headers:
            header_list = []
            for k, v in custom_headers.items():
                key = k.decode() if isinstance(k, bytes) else k
                val = v.decode() if isinstance(v, bytes) else v
                header_list.append({"name": key, "value": val})
            payload["customHttpRequestHeaders"] = header_list
        if body := kwargs.get('body'):
            payload['httpRequestText'] = body 
        try:
            super().__init__(
                url="https://api.zyte.com/v1/extract",
                method="POST",
                headers=headers,
                body=json.dumps(payload),
                meta={**meta,'url': url},
                dont_filter=True,
                callback=kwargs.get('callback') # Avoid duplicate filtering since it's proxied
            )
        except:
            print(payload)


def load(response):
    resp = base64.b64decode(response.json()['httpResponseBody'])
    try:
        response = json.loads(resp)
    except Exception:
        response = Selector(text=resp)
        
    return response       


def time_until_race(race_time_str):
    """
    Returns the time remaining until race starts.
    If race already started, returns 'N/A'.
    
    resp: dict containing 'raceStartTime' as ISO string or timestamp
    """
    if not race_time_str:
        return None
    
    try:
        # Assuming raceStartTime is ISO format string e.g. '2026-02-15T10:00:00Z'
        race_time = datetime.fromisoformat(race_time_str.replace("Z", "+00:00"))
    except ValueError:
        return None
    
    now = datetime.now(timezone.utc)
    delta = race_time - now
    
    if delta.total_seconds() <= 0:
        return None
    
    # Optionally return as HH:MM:SS
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

class UpcomingSpider(scrapy.Spider):
    name = "upcoming"
    races = ['q2 parkland', 'capalaba', 'q straight', 'q1 lakeside', 'ipswich']
    races_dict = {
        'QPD':'ladbrokes-q2-parkland',
        'CPL':'capalaba',
        'QST':'ladbrokes-q-straight',
        'QPD2':'ladbrokes-q1-lakeside',
        'IPS':'ipswich',
    }

    def start_requests(self):
        for date in get_date_list():
            url = f"https://api.beta.tab.com.au/v1/tab-info-service/racing/dates/{date}/meetings?jurisdiction=NSW&returnOffers=true&returnPromo=false"
            yield ZyteRequest(
                url=url,
                callback=self.parse_meetings,
                meta={'date_race': date}
            )
    
    def parse_meetings(self, response):
        resp = load(response)
        for meeting in resp['meetings']:
            if meeting['meetingName'].lower() in self.races:
                for race in meeting['races']:
                    yield ZyteRequest(
                        url=f"https://api.beta.tab.com.au/v1/tab-info-service/racing/dates/{meeting['meetingDate']}/meetings/{meeting['raceType']}/{meeting['venueMnemonic']}/races/{race['raceNumber']}?returnPromo=true&returnOffers=true&jurisdiction={meeting['location']}",
                        callback=self.parse,
                        meta={'date':response.meta['date_race'],'race':self.races_dict[meeting['venueMnemonic']].lower()}
                    )

    def parse(self, response):
        resp = load(response)
        if resp['parimutuelPlaceStatus'].lower() == 'open':
            yield ZyteRequest(
                url=f"https://www.thedogs.com.au/racing/{response.meta['race']}/{response.meta['date']}?trial=false",
                callback=self.parse_all,
                meta={**response.meta , 'resp':resp, 'u':f"https://www.thedogs.com.au/racing/{response.meta['race']}/{response.meta['date']}?trial=false"}
            ) 

    def parse_all(self, response):
        dogs_rsp = load(response)
        resp = response.meta['resp']
        race_number = f"R{resp['raceNumber']}"
        distance = resp['raceDistance']
        url = dogs_rsp.xpath(f"//a[@class='race-header' and contains(.//div/text(),'{race_number}') and contains(.//div[@class='race-header__info__grade']/text(),'{distance}m')]/@href").get()
        if not url:
            for run in resp['runners']:
                dog_name = run['runnerName']
                time = time_until_race(resp['raceStartTime'])
                item = {
                    'track_name':resp['meeting']['meetingName'],
                    'date_of_race':resp['meeting']['meetingDate'],
                    'box_number':run['runnerNumber'],
                    'dog_name':dog_name,
                    'fixed_odds_win':run['fixedOdds']['returnWin'],
                    'fixed_odds_place':run['fixedOdds']['returnPlace'],
                    'time_till_race':time,
                    'race_number':race_number,
                    'race_time':resp['raceStartTime'].split('T')[1].split('.')[0],
                    'race_distance':distance,
                    'grade':resp['raceClassConditions'],
                    'prize_money':resp['prizeMoney'],
                    'whether':f"{resp['meeting']['trackCondition']} {resp['meeting']['weatherCondition']}",
                    'scraped_at': str(datetime.now())
                }
                item['dog_track_dist'] = ''
                item['dog_av_1'] = ''
                item['dog_trainer'] = ''
                item['dog_last_start'] = ''
                yield item
            return
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
            time = time_until_race(resp['raceStartTime'])
            row = dogs_resp.xpath(f'//tr[contains(translate(normalize-space(./td/div//text()), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{dog_name.lower()}")]')
            item = {
                'track_name':resp['meeting']['meetingName'],
                'date_of_race':resp['meeting']['meetingDate'],
                'box_number':run['runnerNumber'],
                'dog_name':dog_name,
                'fixed_odds_win':run['fixedOdds']['returnWin'],
                'fixed_odds_place':run['fixedOdds']['returnPlace'],
                'time_till_race':time,
                'race_number':race_number,
                'race_time':resp['raceStartTime'].split('T')[1].split('.')[0],
                'race_distance':distance,
                'grade':resp['raceClassConditions'],
                'prize_money':resp['prizeMoney'],
                'whether':f"{resp['meeting']['trackCondition']} {resp['meeting']['weatherCondition']}",
                'scraped_at': str(datetime.now())
            }
            item['dog_track_dist'] = ''
            item['dog_av_1'] = ''
            item['dog_trainer'] = ''
            item['dog_last_start'] = ''
            if row:
                item['dog_track_dist'] = row.css('.race-runners__track-dist::text').get()
                item['dog_av_1'] = row.css('.race-runners__speedmap div:nth-child(1)::text').get()
                item['dog_trainer'] = row.css('.race-runners__trainer a::text').get()
                item['dog_last_start'] = '|'.join(row.xpath('.//a[@class="runner-result-cell"]//div//text()').getall())
            yield item

        