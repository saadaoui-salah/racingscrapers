from core.spiders.q_straight_csv import RacingqueenslandCSVSpider


class CaplabaCSVSpider(RacingqueenslandCSVSpider):
    name = 'capalaba_csv'
    race_name = "capalaba"
    csv_url = "https://www.racingqueensland.com.au/industry/harness/harness-sectionals"
    s3_prefix = "/csv/qld-racing/races/capalabe"