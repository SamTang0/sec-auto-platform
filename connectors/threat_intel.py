#!/usr/bin/env python3
import requests
import time
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from common.logger import get_logger

logger = get_logger("threat_intel")

class ThreatIntelClient:
    def __init__(self, abuseipdb_key: str = None):
        self.abuseipdb_key = abuseipdb_key
        self.session = requests.Session()

    def query_abuseipdb(self, ip: str) -> Optional[Dict]:
        if not self.abuseipdb_key:
            return None
        try:
            resp = self.session.get(
                "https://api.abuseipdb.com/api/v2/check",
                headers={"Key": self.abuseipdb_key, "Accept": "application/json"},
                params={"ipAddress": ip, "maxAgeInDays": "90"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json().get('data', {})
                return {
                    'abuse_score': data.get('abuseConfidenceScore', 0),
                    'total_reports': data.get('totalReports', 0),
                    'country': data.get('countryCode', ''),
                    'isp': data.get('isp', '')
                }
        except Exception as e:
            logger.debug(f"AbuseIPDB查询失败 {ip}: {e}")
        return None

    def query_greynoise(self, ip: str) -> Optional[Dict]:
        try:
            resp = requests.get(f"https://api.greynoise.io/v3/community/{ip}", timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'classification': data.get('classification', 'unknown'),
                    'noise': data.get('noise', False),
                    'riot': data.get('riot', False)
                }
        except:
            pass
        return None

    def query_ip_geo(self, ip: str) -> Dict:
        try:
            resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
            data = resp.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', ''),
                    'city': data.get('city', ''),
                    'isp': data.get('isp', ''),
                    'lat': data.get('lat'),
                    'lon': data.get('lon')
                }
        except:
            pass
        return {'country': 'Unknown', 'city': 'Unknown', 'isp': 'Unknown'}

    def analyze_ip(self, ip: str) -> Dict:
        result = {'ip': ip, 'geo': self.query_ip_geo(ip)}
        if self.abuseipdb_key:
            result['abuse'] = self.query_abuseipdb(ip)
        result['greynoise'] = self.query_greynoise(ip)
        if result.get('abuse'):
            score = result['abuse'].get('abuse_score', 0)
            result['risk_level'] = '高危' if score >= 75 else '中危' if score >= 50 else '低危' if score >= 25 else '安全'
            result['risk_score'] = score
        return result

    def batch_analyze(self, ips: List[str], max_workers: int = 10) -> List[Dict]:
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(self.analyze_ip, ip): ip for ip in ips}
            for f in as_completed(futures):
                results.append(f.result())
        return results
