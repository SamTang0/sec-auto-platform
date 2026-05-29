#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from common.logger import get_logger

logger = get_logger("orca")

class OrcaClient:
    def __init__(self, api_url: str, auth_token: str, min_score: float = 7.0):
        self.api_url = api_url
        self.min_score = min_score
        self.session = requests.Session()
        self.session.headers.update({
            'authorization': auth_token,
            'content-type': 'application/json',
            'accept': 'application/json'
        })

    def _post(self, payload: dict) -> dict:
        try:
            resp = self.session.post(self.api_url, json=payload, timeout=30)
            return resp.json()
        except Exception as e:
            logger.error(f"请求失败: {e}")
            return {}

    def query_alerts(self, hours_back: int = 24, limit: int = 100) -> List[Dict]:
        payload = {
            "query": {
                "type": "object_set",
                "with": {
                    "type": "operation",
                    "operator": "and",
                    "values": [
                        {"key": "Status", "type": "str", "values": ["open", "in_progress"], "operator": "in"},
                        {"key": "OrcaScore", "type": "float", "values": [self.min_score], "operator": "gte"}
                    ]
                },
                "models": ["Alert"]
            },
            "limit": limit,
            "order_by[]": ["-OrcaScore"],
            "select": ["AlertId", "Title", "RiskLevel", "OrcaScore", "Status", "CreatedAt"]
        }
        data = self._post(payload)
        items = data.get('results', []) or data.get('data', [])
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)
        filtered = []
        for item in items:
            created = item.get('CreatedAt', '')
            if created:
                try:
                    dt = datetime.strptime(created.replace('Z', '')[:19], "%Y-%m-%dT%H:%M:%S")
                    if dt >= cutoff:
                        filtered.append(item)
                except:
                    filtered.append(item)
        return filtered

    def query_assets(self, hours_back: int = 24, limit: int = 100) -> List[Dict]:
        payload = {
            "query": {
                "type": "object_set",
                "with": {
                    "type": "operation",
                    "operator": "and",
                    "values": [
                        {"key": "Type", "type": "str", "values": ["NewDomain", "NewIP"], "operator": "in"}
                    ]
                },
                "models": ["Inventory"]
            },
            "limit": limit,
            "order_by[]": ["-OrcaScore"],
            "select": ["Name", "Type", "RiskLevel", "OrcaScore", "FirstSeen", "IsInternetFacing"]
        }
        data = self._post(payload)
        items = data.get('results', []) or data.get('data', [])
        cutoff = datetime.utcnow() - timedelta(hours=hours_back)
        filtered = []
        for item in items:
            first = item.get('FirstSeen', '')
            if first:
                try:
                    dt = datetime.strptime(first.replace('Z', '')[:19], "%Y-%m-%dT%H:%M:%S")
                    if dt >= cutoff:
                        filtered.append(item)
                except:
                    filtered.append(item)
        return filtered
