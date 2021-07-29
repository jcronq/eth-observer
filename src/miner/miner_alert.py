import os

import boto3
from utils.events import global_event

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
AWS_PUBLISH_TOPIC_ARN = os.getenv('AWS_PUBLISH_TOPIC_ARN')

client = boto3.client(
    'sns',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@global_event("miner_unavailable")
async def _miner_unavailable(miner_ip):
    print(f"SNS Notified miner_offline")
    client.publish(
        TopicArn=AWS_PUBLISH_TOPIC_ARN,
        Message=f'{miner_ip} has been offline for 60s.',
    )

@global_event("miner_available")
async def _miner_available(miner_ip):
    print(f"SNS Notified miner_online")
    client.publish(
        TopicArn=AWS_PUBLISH_TOPIC_ARN,
        Message=f'{miner_ip} is back online.',
    )

@global_event("miner_restarted")
async def _miner_restarted(miner_ip):
    print(f"SNS Notified miner_restarted")
    client.publish(
        TopicArn=AWS_PUBLISH_TOPIC_ARN,
        Message=f'{miner_ip} was (re)started.',
    )
