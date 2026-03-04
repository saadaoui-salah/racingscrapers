from core.spiders.q_straight_csv import RacingqueenslandCSVSpider


class ParklandsCSVSpider(RacingqueenslandCSVSpider):
    name = 'parklands_csv'
    race_name = "q2 parklands"
    s3_prefix = "/csv/qld-racing/races/parklands"

