from core.spiders.q_straight_csv import RacingqueenslandCSVSpider


class IpswichCSVSpider(RacingqueenslandCSVSpider):
    name = 'ipswich_csv'
    race_name = "ipswich"
    csv_url = "https://www.racingqueensland.com.au/industry/harness/harness-sectionals"
    s3_prefix = "/csv/qld-racing/races/ipswich"