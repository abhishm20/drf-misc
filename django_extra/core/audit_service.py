# -*- coding: utf-8 -*-
import json
import os
import time
import boto3
from django_extra.settings import app_settings


class AuditService:
    def __init__(self):
        self.client = boto3.client(
            'sqs',
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
        )
    
    def send_event(self, action, entity, data, request, is_critical=False, remark=None):
        body = {
            "is_critical": is_critical,
            "timestamp": str(int(time.time())),
            "action": action,
            "data": data,
            "entity": entity,
            "remark": remark,
        }
        self._push_to_queue(body, request)
    
    def _push_to_queue(self, body, request):
        body['header'] = {
            'auth_token': request.META.get('HTTP_AUTHORIZATION'),
            'source_ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT')
        }
        return self.client.send_message(
            QueueUrl=app_settings.audit_queue_url,
            MessageBody=json.dumps(body),
            MessageGroupId=app_settings.service_name,
        )