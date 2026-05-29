#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import load_config
from common.logger import get_logger
from connectors.aws_client import AWSClient

logger = get_logger("waf")

def main():
    print("=" * 60)
    print("AWS WAF 日志分析")
    print("=" * 60)
    config = load_config()
    if not config.aws.log_group:
        print("错误: 请配置 WAF_LOG_GROUP")
        return

    client = AWSClient(config.aws.profile, config.aws.region)
    results = client.query_waf_logs(config.aws.log_group, config.aws.webacl_id)

    if results:
        print(f"\n共 {len(results)} 条拦截记录\n")
        print(f"{'IP':<20} {'URI':<50} {'次数':<10}")
        print("-" * 80)
        for r in results[:20]:
            print(f"{r.get('httpRequest.clientIp', ''):<20} {r.get('httpRequest.uri', '')[:50]:<50} {r.get('cnt', 0):<10}")
    else:
        print("未发现拦截记录")

if __name__ == "__main__":
    main()
