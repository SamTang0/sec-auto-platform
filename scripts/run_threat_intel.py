#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import load_config
from common.logger import get_logger
from connectors.threat_intel import ThreatIntelClient

logger = get_logger("threat_intel")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='IP列表文件')
    parser.add_argument('-i', '--ip', help='单个IP')
    parser.add_argument('-o', '--output', help='输出文件')
    args = parser.parse_args()

    ips = []
    if args.ip:
        ips = [args.ip]
    elif args.file:
        with open(args.file) as f:
            ips = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    else:
        print("请输入IP（每行一个，空行结束）:")
        while True:
            ip = input().strip()
            if not ip:
                break
            ips.append(ip)

    if not ips:
        print("没有IP需要查询")
        return

    config = load_config()
    client = ThreatIntelClient(config.threat_intel.abuseipdb_key)

    print(f"\n查询 {len(ips)} 个IP...\n")
    for ip in ips:
        result = client.analyze_ip(ip)
        geo = result.get('geo', {})
        print(f"{ip:20} | {geo.get('country', 'N/A'):12} | {geo.get('city', 'N/A'):12} | 风险: {result.get('risk_level', 'N/A')}")

if __name__ == "__main__":
    main()
