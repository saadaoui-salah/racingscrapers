import os

import dropbox
from scrapy import signals
from datetime import datetime
import boto3
from scrapy import signals


class DropboxUploadExtension:

    def __init__(self, access_token, file_path, dropbox_target):
        self.access_token = access_token
        self.file_path = file_path
        self.dropbox_target = dropbox_target

    @classmethod
    def from_crawler(cls, crawler):
        access_token = crawler.settings.get("DROPBOX_ACCESS_TOKEN")
        file_path = crawler.settings.get("UPLOAD_FILE_PATH")  # local CSV exported by Feed
        dropbox_target = crawler.settings.get("DROPBOX_UPLOAD_PATH", f"/export-{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")

        ext = cls(access_token, file_path, dropbox_target)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        return ext

    def spider_closed(self, spider):
        print("🚀 Spider closed — uploading CSV to Dropbox...")

        try:
            dbx = dropbox.Dropbox(self.access_token)
            with open(self.file_path, "rb") as f:
                dbx.files_upload(
                    f.read(),
                    self.dropbox_target,
                    mode=dropbox.files.WriteMode.overwrite,
                )
            spider.logger.info(f"✅ Uploaded to Dropbox: {self.dropbox_target}")
        except Exception as e:
            spider.logger.error(f"❌ Dropbox upload failed: {e}")




class S3UploadExtension:

    def __init__(self, access_key, secret_key, bucket, file_path, spider_name):
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.file_path = file_path
        self.spider_name = spider_name  # store spider name

    @classmethod
    def from_crawler(cls, crawler):
        access_key = crawler.settings.get("AWS_ACCESS_KEY_ID")
        secret_key = crawler.settings.get("AWS_SECRET_ACCESS_KEY")
        bucket = crawler.settings.get("S3_BUCKET")

        # Detect output file automatically
        file_path = None
        feeds = crawler.settings.get("FEEDS")
        if feeds:
            file_path = list(feeds.keys())[0]
        if not file_path:
            file_path = crawler.settings.get("FEED_URI")
        if not file_path:
            raise Exception("❌ Could not detect output file (FEEDS / -o not set)")

        ext = cls(access_key, secret_key, bucket, file_path, crawler.spider.name)
        crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)
        return ext

    def engine_stopped(self):
        print("🚀 Engine stopped — uploading output file to S3...")
        s3_prefix = "unity-catalog/652267796750120/CSV/qld-racing/races"

        try:
            if not os.path.exists(self.file_path):
                print(f"❌ Output file not found: {self.file_path}")
                return

            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )

            filename = os.path.basename(self.file_path)
            s3_key = f"{s3_prefix}/{self.spider_name.replace('_csv','')}/{filename}"

            s3.upload_file(self.file_path, self.bucket, s3_key)
            print(f"✅ Uploaded to S3: s3://{self.bucket}/{s3_key}")

            # Delete the local file after upload
            os.remove(self.file_path)
            print(f"🗑 Deleted local file: {self.file_path}")

        except Exception as e:
            print(f"❌ S3 upload failed: {e}")