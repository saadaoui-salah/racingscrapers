from core.spiders.q_straight import RacingqueenslandSpider


class ParklandsSpider(RacingqueenslandSpider):
    url_filter = 'qtt%20'
    name = "parklands"