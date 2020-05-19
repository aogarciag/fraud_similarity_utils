import boto3
import io
import gzip
import os
import pandas as pd

class S3Exception(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class S3:
    AWS_KEY = os.environ.get("AWS_KEY", None)
    AWS_SECRET = os.environ.get("AWS_SECRET", None)
    SSE_KMS_KEY_ID = os.environ.get("AWS_SSE_KMS_KEY_ID", None)
    BUCKET = os.environ.get("AWS_BUCKET", None)
    REGION = os.environ.get("AWS_REGION", None)

    kms = boto3.Session(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET, region_name=REGION).client('kms')
    s3 = boto3.Session(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET, region_name=REGION).client('s3')

    @classmethod
    def upload_file(cls,file_path,key):
        try:
            cls.s3.upload_file(file_path, cls.BUCKET, key,
                                          ExtraArgs={"ServerSideEncryption": "aws:kms", "SSEKMSKeyId": cls.SSE_KMS_KEY_ID})
        except Exception as e:
            print(e)
            raise S3Exception("s3_failed_upload_file")

    @classmethod
    def download_file(cls,key):
        try:
            file=cls.s3.get_object(Bucket=cls.BUCKET, Key=key)
        except:
            raise S3Exception("s3_failed_download_file")
        return file

    @classmethod
    def pandas_to_s3(cls,df,key):
        # write DF to string stream
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # reset stream position
        csv_buffer.seek(0)
        # create binary stream
        gz_buffer = io.BytesIO()

        # compress string stream using gzip
        with gzip.GzipFile(mode='w', fileobj=gz_buffer) as gz_file:
            gz_file.write(bytes(csv_buffer.getvalue(), 'utf-8'))
            
        # write stream to S3
        cls.s3.put_object(Bucket=cls.BUCKET, Key=key, Body=gz_buffer.getvalue())

    @classmethod
    def s3_to_pandas(cls,key, header=None):

        # get key using boto3 client
        obj = cls.s3.get_object(Bucket=cls.BUCKET, Key=key)
        gz = gzip.GzipFile(fileobj=obj['Body'])
        
        # load stream directly to DF
        return pd.read_csv(gz, header=header, dtype=str)

    @classmethod
    def s3_to_pandas_with_processing(cls, key, header=None):
        
        # get key using boto3 client
        obj = cls.s3.get_object(Bucket=cls.BUCKET, Key=key)
        gz = gzip.GzipFile(fileobj=obj['Body'])

        # replace some characters in incomming stream and load it to DF
        lines = "\n".join([line.replace('?', ' ') for line in gz.read().decode('utf-8').split('\n')])
        return pd.read_csv(io.StringIO(lines), header=None, dtype=str)
