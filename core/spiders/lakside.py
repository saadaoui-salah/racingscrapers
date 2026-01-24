from core.spiders.q_straight import RacingqueenslandSpider


class LaksideSpider(RacingqueenslandSpider):
    url_filter = 'qot%20'
    name = "lakside"
