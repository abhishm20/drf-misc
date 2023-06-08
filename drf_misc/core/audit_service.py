# -*- coding: utf-8 -*-
import copy
import json
import os
import time

import boto3
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from drf_misc.settings import app_settings

app_logger = getattr(settings, "app_logger", None)


class AuditService:
    def __init__(self):
        self.client = boto3.client(
            "sqs",
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
        )

    def send_event(self, entity, data, request, audit_data):
        for key in copy.deepcopy(data):
            if isinstance(data[key], InMemoryUploadedFile):
                del data[key]
        body = {
            "timestamp": str(int(time.time())),
            "data": data,
            "entity": entity,
        }
        body.update(audit_data)
        self._push_to_queue(body, request)

    def _push_to_queue(self, body, request):
        body["headers"] = {
            "auth_token": request.META.get("HTTP_AUTHORIZATION")
            if request
            else "System",
            "source_ip": request.META.get("REMOTE_ADDR") if request else "System",
            "user_agent": request.META.get("HTTP_USER_AGENT") if request else "System",
        }
        res = self.client.send_message(
            QueueUrl=app_settings.audit_queue_url,
            MessageBody=json.dumps(body),
            MessageGroupId=app_settings.service_name,
        )
        if app_logger:
            app_logger.info(
                "Event push to Audit SQS: payload: %s, response: %s", body, res
            )
        return res
