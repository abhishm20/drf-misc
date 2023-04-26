# -*- coding: utf-8 -*-
import json
import os
import time
import boto3
from django_extra.settings import app_settings

class AWSApi:
    def __init__(self, service_name):
        self.client = boto3.client(
            service_name,
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
        )

    def send_message(self, inserted, request=dict, remark="", action="", data=""):
        body = {
            "is_critical": True,
            "timestamp":str(int(time.time())),
            "action": action,
            "data": data,
            "meta": {
                "entity_id": inserted.id,
                "entity_name": inserted.__class__.__name__,
                "service_name": app_settings.SERVICE_NAME,
            },
            "remark": remark,
            "user": {
                "user_id": request.auth_user.get("user_id")
                if hasattr(request, "auth_user")
                else None
            },
        }
        return self.client.send_message(
            QueueUrl=app_settings.CONFIG_SECRET.get(
                "audit_queue_uri",
                "https://sqs.ap-south-1.amazonaws.com/659590398921/dev-crego-audit-log-queue.fifo",
            ),
            MessageBody=json.dumps(body),
            MessageGroupId=app_settings.SERVICE_NAME,
        )