from core.spiders.q_straight import RacingqueenslandSpider


class AlbionSpider(RacingqueenslandSpider):
    url_filter = 'albi'
    name = "albion"
    