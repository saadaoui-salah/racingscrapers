import scrapy
import io
import csv
from scrapy import Request
from datetime import datetime, timedelta




class RacingqueenslandCSVSpider(scrapy.Spider):
    name = "q_straight_csv"
    s3_prefix = "csv/qld-racing/races/q_straight"
    race_name = "q straight"
    csv_url = "https://www.racingqueensland.com.au/industry/greyhound/greyhound-sectionals"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Sec-CH-UA": '"Chromium";v="141", "Google Chrome";v="141", "Not(A:Brand";v="24"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Linux"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }

    #def get_slugs(self):
    #    result = []
    #    current = datetime.now()
    #    end = datetime(current.year - 1, 10, 1)  # last year October
    #    while current >= end:
    #        result.append(current.strftime("%Y/%m"))
    #        # Go back one month:
    #        first_day_this_month = current.replace(day=1)
    #        current = first_day_this_month - timedelta(days=1)
    #    return result


    def get_slugs(self):
        result = []
        today = datetime.now()

        for i in range(4):  # today + last 2 days
            day = today - timedelta(days=i)
            result.append(day.strftime("%d/%m/%Y"))

        return result

    def start_requests(self):
            yield scrapy.Request(
                url="https://www.racingqueensland.com.au/industry/greyhound/greyhound-sectionals",
                headers=self.headers,
                callback=self.parse,
            )


    def parse(self, response):
        dates = self.get_slugs()
        for race in response.css('.c-accordion__list__list li'):
            title = race.css('span::text').get().lower()
            if title.split()[0] in dates and self.race_name.lower() in title.lower():
                link = race.xpath('//a[@class="c-accordion__list__item__link" and contains(text(), "CSV")]/@href').get()
                yield Request(
                     url=f"https://www.racingqueensland.com.au{link}",
                     headers=self.headers,
                     callback=self.parse_csv
                ) 

    def parse_csv(self, response):
        csv_text = response.text
        csv_file = io.StringIO(csv_text)
        reader = csv.DictReader(csv_file)
        for row in reader:
            row['filename'] = response.url.split('/')[-1]
            yield row