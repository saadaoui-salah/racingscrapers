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

    def __init__(self, access_key, secret_key, file_path, bucket, s3_prefix):
        self.access_key = access_key
        self.secret_key = secret_key
        self.file_path = file_path
        self.bucket = bucket
        self.s3_prefix = s3_prefix.rstrip("/") + "/"

    @classmethod
    def from_crawler(cls, crawler):
        access_key = crawler.settings.get("AWS_ACCESS_KEY_ID")
        secret_key = crawler.settings.get("AWS_SECRET_ACCESS_KEY")
        file_path = crawler.settings.get("UPLOAD_FILE_PATH")  # local CSV path

        bucket = crawler.settings.get("S3_BUCKET")
        s3_prefix = crawler.settings.get(
            "S3_PREFIX",
            f"unity-catalog/652267796750120/CSV/{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        ext = cls(access_key, secret_key, file_path, bucket, s3_prefix)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        return ext

    def spider_closed(self, spider):
        spider.logger.info("🚀 Spider closed — uploading CSV to S3...")

        try:
            # Create S3 client
            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )

            # Choose a name inside S3
            s3_key = f"{self.s3_prefix}_{spider.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

            # Upload
            s3.upload_file(self.file_path, self.bucket, s3_key)

            spider.logger.info(f"✅ Uploaded to S3: s3://{self.bucket}/{s3_key}")

        except Exception as e:
            spider.logger.error(f"❌ S3 upload failed: {e}")