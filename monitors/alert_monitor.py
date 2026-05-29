from common.logger import get_logger
from common.webhook import WebhookPusher
from common.excel_export import ExcelExporter
from connectors.orca_client import OrcaClient

logger = get_logger("alert_monitor")

class AlertMonitor:
    def __init__(self, config, webhook_url: str = None):
        self.client = OrcaClient(config.api_url, config.auth_token, config.min_score)
        self.webhook = WebhookPusher(webhook_url) if webhook_url else None
        self.exporter = ExcelExporter()

    def scan(self) -> list:
        logger.info("扫描告警...")
        alerts = self.client.query_alerts()
        if alerts:
            logger.info(f"发现 {len(alerts)} 条告警")
            self.exporter.export_alerts(alerts)
            if self.webhook:
                msg = f"**告警数量**: {len(alerts)}\n"
                for a in alerts[:5]:
                    msg += f"- [{a.get('RiskLevel')}] {a.get('Title', '')[:50]}\n"
                self.webhook.send_markdown(msg, "安全告警")
        else:
            logger.info("未发现新告警")
        return alerts
