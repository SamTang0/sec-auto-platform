#!/usr/bin/env python3
import boto3
import time
from datetime import datetime, timedelta
from typing import List, Dict
from common.logger import get_logger

logger = get_logger("aws")

class AWSClient:
    def __init__(self, profile: str = None, region: str = "us-east-1"):
        if profile:
            self.session = boto3.Session(profile_name=profile, region_name=region)
        else:
            self.session = boto3.Session(region_name=region)
        self.logs = self.session.client('logs')

    def query_waf_logs(self, log_group: str, webacl_id: str, hours_back: int = 24, limit: int = 10000) -> List[Dict]:
        end = datetime.now()
        start = end - timedelta(hours=hours_back)
        query = f'''
        fields @timestamp, httpRequest.clientIp, httpRequest.uri, action, terminatingRuleId
        | filter webaclId = "{webacl_id}" and action = "BLOCK"
        | stats count() as cnt by httpRequest.clientIp, httpRequest.uri
        | sort cnt desc
        | limit {limit}
        '''
        try:
            resp = self.logs.start_query(
                logGroupName=log_group,
                startTime=int(start.timestamp() * 1000),
                endTime=int(end.timestamp() * 1000),
                queryString=query,
                limit=limit
            )
            qid = resp['queryId']
            for _ in range(30):
                time.sleep(2)
                result = self.logs.get_query_results(queryId=qid)
                if result['status'] == 'Complete':
                    rows = []
                    for row in result['results']:
                        item = {}
                        for f in row:
                            item[f['field']] = f['value']
                        rows.append(item)
                    return rows
        except Exception as e:
            logger.error(f"WAF查询失败: {e}")
        return []
