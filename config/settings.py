import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent

@dataclass
class OrcaConfig:
    api_url: str = os.environ.get("ORCA_API_URL", "")
    auth_token: str = os.environ.get("ORCA_AUTH_TOKEN", "")
    business_units: List[str] = field(default_factory=lambda: ["UNIT_A", "UNIT_B"])
    min_score: float = 7.0

@dataclass
class AWSConfig:
    region: str = os.environ.get("AWS_REGION", "us-east-1")
    profile: str = os.environ.get("AWS_PROFILE", "")
    log_group: str = os.environ.get("WAF_LOG_GROUP", "")
    webacl_id: str = os.environ.get("WAF_WEBACL_ID", "")

@dataclass
class ChaitinConfig:
    base_url: str = os.environ.get("CHAITIN_BASE_URL", "")
    session: str = os.environ.get("CHAITIN_SESSION", "")
    workspace: str = os.environ.get("CHAITIN_WORKSPACE", "1")

@dataclass
class WebhookConfig:
    url: str = os.environ.get("WEBHOOK_URL", "")

@dataclass
class ThreatIntelConfig:
    abuseipdb_key: str = os.environ.get("ABUSEIPDB_API_KEY", "")

@dataclass
class AppConfig:
    orca: OrcaConfig = field(default_factory=OrcaConfig)
    aws: AWSConfig = field(default_factory=AWSConfig)
    chaitin: ChaitinConfig = field(default_factory=ChaitinConfig)
    webhook: WebhookConfig = field(default_factory=WebhookConfig)
    threat_intel: ThreatIntelConfig = field(default_factory=ThreatIntelConfig)
    scan_interval: int = int(os.environ.get("SCAN_INTERVAL_HOURS", "12"))
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")

def load_config() -> AppConfig:
    return AppConfig()
