from core.spiders.q_straight import RacingqueenslandSpider


class IpswichSpider(RacingqueenslandSpider):
    url_filter = 'ipsw'
    name = "ipswich"
    event_code = 'thoroughbred'
