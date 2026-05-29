import requests
from typing import List, Dict
from .logger import get_logger

logger = get_logger("webhook")

class WebhookPusher:
    def __init__(self, url: str, mention_users: List[str] = None):
        self.url = url
        self.mention_users = mention_users or []
        self.enabled = bool(url)

    def send_text(self, text: str) -> bool:
        if not self.enabled:
            return False
        try:
            r = requests.post(self.url, json={"text": text}, timeout=10)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"发送失败: {e}")
            return False

    def send_markdown(self, content: str, title: str = "") -> bool:
        if not self.enabled:
            return False
        full = f"## {title}\n{content}" if title else content
        try:
            r = requests.post(self.url, json={"msgtype": "markdown", "markdown": {"content": full}}, timeout=10)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"发送失败: {e}")
            return False

    def send_table(self, headers: List[str], rows: List[List[str]], title: str = "") -> bool:
        if not rows:
            return False
        col_w = [max(len(str(h)), max((len(str(r[i])) for r in rows[:10]), default=0)) for i, h in enumerate(headers)]
        lines = ["| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_w)) + " |"]
        lines.append("|" + "|".join("-" * (w + 2) for w in col_w) + "|")
        for row in rows[:20]:
            lines.append("| " + " | ".join(str(c).ljust(w) for c, w in zip(row, col_w)) + " |")
        if len(rows) > 20:
            lines.append(f"... 共 {len(rows)} 行")
        return self.send_markdown("\n".join(lines), title)
