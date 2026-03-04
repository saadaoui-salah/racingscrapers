from core.spiders.q_straight_csv import RacingqueenslandCSVSpider


class LakesideCSVSpider(RacingqueenslandCSVSpider):
    name = 'lakeside_csv'
    race_name = "q1 lakeside"
    s3_prefix = "/csv/qld-racing/races/lakeside"