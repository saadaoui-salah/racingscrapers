import scrapy
import io
import pdfplumber
import os
import base64
import json
from scrapy import Request, Selector
import random
from datetime import datetime, timedelta
import logging
logging.getLogger("pdfminer").disabled = True


class ZyteRequest(Request):
    def __init__(self, url, meta={}, *args, **kwargs):
        api_key = os.getenv("ZYTE_API")
        if not api_key:
            raise ValueError("ZYTE_API environment variable not set")

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
            "geolocation":"US",
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
                callback=kwargs.get('callback')  # Avoid duplicate filtering since it's proxied
            )
        except:
            print(payload)


def load(response):
    response = base64.b64decode(response.json()['httpResponseBody'])
    try:
        response = json.loads(response)
    except Exception:
        response = Selector(text=response)
        
    return response       

def pdf_to_table(content):
    file_like_pdf = io.BytesIO(content)  # create a file-like object

    with pdfplumber.open(file_like_pdf) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            print(f"Page {page_number}")
            for table in tables:
                for row in table:
                    print(row)
            print("-" * 40)

class RacingqueenslandSpider(scrapy.Spider):
    name = "q_straight"
    start_urls = ["https://racingqueensland.com.au/racing/full-calendar/"]
    url_filter = 'qst'
    custom_settings = {
        'UPLOAD_FILE_PATH':f"{name}.csv"
    }
    event_code = 'greyhound'

    def get_slugs(self):

        result = []
        current = datetime.now()
        end = datetime(current.year - 1, 10, 1)  # last year October

        while current >= end:
            result.append(current.strftime("%Y/%m"))
            # Go back one month:
            first_day_this_month = current.replace(day=1)
            current = first_day_this_month - timedelta(days=1)

        return result

    def start_requests(self):
        for slug in self.get_slugs():
            yield scrapy.Request(
                url=f"https://www.racingqueensland.com.au/racing/full-calendar/{slug}",
                callback=self.parse,
            )


    def parse(self, response):
        urls = response.css(f'[data-js-calendar-events-code="{self.event_code}"] .s-race-calendar__grid__event > a::attr(href)').getall()
        for url in urls:
            if self.url_filter in url:
                yield scrapy.Request(
                    url=f"https://racingqueensland.com.au{url}",
                    callback=self.parse_details,
                )

    def parse_details(self, repsonse):
        race_link = repsonse.xpath('//a[@class="c-race-downloads__link" and contains(./span, "Meeting Sectionals PDF")]/@href').get()
        if race_link:
            yield scrapy.Request(
                url=f"https://racingqueensland.com.au{race_link}",
                callback=self.parse_results,
            )

    def format_time(self, text):
        raw = text[2].split(' - ')[-1].strip()
        parts = raw.split(":")
        hour = int(parts[0])

        if hour > 12:  # probably 24-hour format with PM incorrectly attached
            raw = raw.replace(" PM", "").replace(" AM", "")
            return raw  # already in correct format
        else:
            t = datetime.strptime(raw, "%I:%M:%S %p")
            return t.strftime("%H:%M:%S")

    def get_to_rail(self, row):
        try:
            return row.split('\n')[2].split('(')[1][:-1]
        except:
            return '--'

    def parse_results(self, response):
        file_like_pdf = io.BytesIO(response.body)
        race = response.url.split('/')[-1].split('_')[:2]
        with pdfplumber.open(file_like_pdf) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text().split('\n')
                tables = page.extract_tables()
                race_number = text[1].split('-')[0].replace('Race','').strip()
                for table in tables:
                    # Convert each row into a Scrapy item-like dict
                    for i, row in enumerate(table, start=1):
                        try:
                            item =  {
                                "Race_time": self.format_time(text),
                                "Race_Title": text[1].split('-')[1].strip(),
                                "distance": '300M',
                                "Race_number": race_number,
                                "Date": text[2].split(' - ')[0].strip(),
                                "State": text[0].split(',')[1].strip(),
                                "Track": ''.join(text[0].split(',')[0].split(' ')[1:]).strip(),
                                "Race_ID": f'{race[0]}_{race[1]}_{race_number}',
                                "Dog_Name": row[1] if row[1].lower() != 'race' else '',
                                "Box": row[2],
                                "Placing": i,
                                "Finish_time": row[-1].split('[')[0],
                                "Top_speed_KMH": row[3].split('KM')[0],
                                
                                "50m_time": row[4].split('\n')[0].split('[')[0],
                                "50m_speed": row[4].split('\n')[1].replace('KM/H',''),
                                "section_50_meters_to_rail_for_section": self.get_to_rail(row[4]),
                                "sec_50_rank":row[4].split('\n')[0].split('[')[1].split(']')[0],
                                
                                "100m_time": row[5].split('\n')[0].split('[')[0],
                                "100m_speed": row[5].split('\n')[1].replace('KM/H',''),
                                "section_100_meters_to_rail_for_section": self.get_to_rail(row[5]),
                                "sec_100_rank":row[5].split('\n')[0].split('[')[1].split(']')[0],
                                
                                "150m_time": row[6].split('\n')[0].split('[')[0],
                                "150m_speed": row[6].split('\n')[1].replace('KM/H',''),
                                "section_150_meters_to_rail_for_section": self.get_to_rail(row[6]),
                                "sec_150_rank":row[6].split('\n')[0].split('[')[1].split(']')[0],
                                
                                "200m_time": row[7].split('\n')[0].split('[')[0],
                                "200m_speed": row[7].split('\n')[1].replace('KM/H',''),
                                "section_200_meters_to_rail_for_section": self.get_to_rail(row[7]),
                                "sec_200_rank":row[7].split('\n')[0].split('[')[1].split(']')[0],
                                
                                "250m_time": row[8].split('\n')[0].split('[')[0],
                                "250m_speed": row[8].split('\n')[1].replace('KM/H',''),
                                "section_250_meters_to_rail_for_section": self.get_to_rail(row[8]),
                                "sec_250_rank":row[8].split('\n')[0].split('[')[1].split(']')[0],
                                
                                "300m_time": row[9].split('\n')[0].split('[')[0],
                                "300m_speed": row[9].split('\n')[1].replace('KM/H',''),
                                "section_300_meters_to_rail_for_section": self.get_to_rail(row[9]),
                                "sec_300_rank":row[9].split('\n')[0].split('[')[1].split(']')[0],
                                
                                "Run_home": row[10].split('\n')[0].split('[')[0],
                                "Hme_speed": row[10].split('\n')[1].replace('KM/H',''),
                            }
                            if len(row) == 13:
                                item["distance"] = "350M"
                                item["350m_time"] = row[10].split('\n')[0].split('[')[0]
                                item["350m_speed"] = row[10].split('\n')[1].replace('KM/H','')
                                item["section_350_meters_to_rail_for_section"] = self.get_to_rail(row[10])
                                item["sec_300_rank"] = row[10].split('\n')[0].split('[')[1].split(']')[0]
                                item["Run_home"] = row[11].split('\n')[0].split('[')[0]
                                item["Hme_speed"] = row[11].split('\n')[1].replace('KM/H','')
                            yield item
                        except: 
                            breakpoint()