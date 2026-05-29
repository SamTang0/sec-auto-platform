#!/usr/bin/env python3
import sys
import time
import schedule
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import load_config
from common.logger import get_logger
from monitors.alert_monitor import AlertMonitor
from monitors.asset_monitor import AssetMonitor

logger = get_logger("main")

def main():
    print("=" * 60)
    print("Orca Security 监控服务")
    print("=" * 60)
    config = load_config()
    if not config.orca.auth_token:
        print("错误: 请配置 .env 文件中的 ORCA_AUTH_TOKEN")
        return
    alert = AlertMonitor(config.orca, config.webhook.url)
    asset = AssetMonitor(config.orca, config.webhook.url)

    def run():
        alert.scan()
        asset.scan()

    run()
    schedule.every(config.scan_interval).hours.do(run)
    logger.info(f"调度启动，间隔 {config.scan_interval} 小时")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("服务停止")

if __name__ == "__main__":
    main()
