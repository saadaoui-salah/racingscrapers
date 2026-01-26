from core.spiders.q_straight import RacingqueenslandSpider


class ParklandsSpider(RacingqueenslandSpider):
    url_filter = 'qtt%20'
    name = "parklands"
    custom_settings = {
        'UPLOAD_FILE_PATH':f"{name}.csv"
    }