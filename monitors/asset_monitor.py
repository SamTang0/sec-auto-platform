from common.logger import get_logger
from common.webhook import WebhookPusher
from common.excel_export import ExcelExporter
from connectors.orca_client import OrcaClient

logger = get_logger("asset_monitor")

class AssetMonitor:
    def __init__(self, config, webhook_url: str = None):
        self.client = OrcaClient(config.api_url, config.auth_token, config.min_score)
        self.webhook = WebhookPusher(webhook_url) if webhook_url else None
        self.exporter = ExcelExporter()

    def scan(self) -> list:
        logger.info("扫描资产...")
        assets = self.client.query_assets()
        if assets:
            logger.info(f"发现 {len(assets)} 个新资产")
            self.exporter.export_assets(assets)
            if self.webhook:
                internet = sum(1 for a in assets if a.get('IsInternetFacing'))
                msg = f"**新增资产**: {len(assets)}\n**公网暴露**: {internet}\n"
                for a in assets[:5]:
                    msg += f"- {a.get('Name')} [{a.get('RiskLevel')}]\n"
                self.webhook.send_markdown(msg, "资产发现")
        else:
            logger.info("未发现新资产")
        return assets
