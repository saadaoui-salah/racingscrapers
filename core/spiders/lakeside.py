from core.spiders.q_straight import RacingqueenslandSpider


class LakesideSpider(RacingqueenslandSpider):
    url_filter = 'qot%20'
    name = "lakeside"
