import boto3
import datetime
from decouple import config

# Initialize a session using Amazon S3
s3 = boto3.client(
        's3',
        aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'),
        region_name= config('AWS_S3_REGION_NAME')
    )

# Replace with your bucket name
bucket_name = config('AWS_STORAGE_BUCKET_NAME')

# Calculate 48 hours ago from now
time_threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=48)

# List all objects in the bucket
response = s3.list_objects_v2(Bucket=bucket_name)

if 'Contents' in response:
    for obj in response['Contents']:
        # Get the last modified time of each object
        last_modified = obj['LastModified']

        # If the file is older than 24 hours, delete it
        if last_modified < time_threshold:
            print(f"Deleting file: {obj['Key']} (Last modified: {last_modified})")
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
else:
    print("No files found in the bucket.")


# Open the Crontab File:
# crontab -e


# Add a cron job to run the script every 6 hours:
# 0 */6 * * * /usr/bin/python3 /home/ubuntu/filesharing/delete_S3_bucket__old_objects.py


# Verify the Cron Job: List scheduled cron jobs to confirm:
# crontab -l