from core.spiders.q_straight import RacingqueenslandSpider


class LakesideSpider(RacingqueenslandSpider):
    url_filter = 'qot%20'
    name = "lakeside"
    custom_settings = {
        'UPLOAD_FILE_PATH':f"{name}.csv"
    }
