from core.spiders.q_straight_csv import RacingqueenslandCSVSpider


class AlbionCSVSpider(RacingqueenslandCSVSpider):
    name = 'albion_csv'
    race_name = "albion park"
    csv_url = "https://www.racingqueensland.com.au/industry/harness/harness-sectionals"
    s3_prefix = "/csv/qld-racing/races/albion"
