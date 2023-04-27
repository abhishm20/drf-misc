# -*- coding: utf-8 -*-
import json
import os
import time
import boto3
from django_extra.settings import app_settings
from django.conf import settings

app_logger = getattr(settings, 'app_logger', None)

class AuditService:
    def __init__(self):
        self.client = boto3.client(
            'sqs',
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
        )
    
    def send_event(self, action, entity, data, request, level="trace", remark=""):
        body = {
            "level": level,
            "timestamp": str(int(time.time())),
            "action": action,
            "data": data,
            "entity": entity,
            "remark": remark,
        }
        self._push_to_queue(body, request)
    
    def _push_to_queue(self, body, request):
        body['headers'] = {
            'auth_token': request.META.get('HTTP_AUTHORIZATION'),
            'source_ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT')
        }
        res =  self.client.send_message(
            QueueUrl=app_settings.audit_queue_url,
            MessageBody=json.dumps(body),
            MessageGroupId=app_settings.service_name,
        )
        if app_logger:
            app_logger.info("Event push to Audit SQS: payload: %s, response: %s", body, res)
        return res
        