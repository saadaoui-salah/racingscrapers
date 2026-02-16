from core.spiders.q_straight import RacingqueenslandSpider


class CapalabaSpider(RacingqueenslandSpider):
    url_filter = 'capa'
    name = "capalaba"
