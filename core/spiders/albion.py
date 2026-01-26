from core.spiders.q_straight import RacingqueenslandSpider


class AlbionSpider(RacingqueenslandSpider):
    url_filter = 'albi'
    name = "albion"
    event_code = 'harness'
    custom_settings = {
        'UPLOAD_FILE_PATH':f"{name}.csv"
    }