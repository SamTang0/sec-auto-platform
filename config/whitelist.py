import ipaddress
from pathlib import Path
from typing import Tuple, Optional, List

class WhitelistManager:
    def __init__(self, whitelist_file: Path = None):
        self.whitelist_file = whitelist_file or Path("./whitelist.txt")
        self.networks: List[ipaddress.IPv4Network] = []
        self._load()

    def _load(self):
        if self.whitelist_file.exists():
            with open(self.whitelist_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            self.networks.append(ipaddress.ip_network(line, strict=False))
                        except:
                            pass

    def is_whitelisted(self, ip: str) -> Tuple[bool, Optional[str]]:
        try:
            ip_obj = ipaddress.ip_address(ip)
            for net in self.networks:
                if ip_obj in net:
                    return True, str(net)
        except:
            pass
        return False, None
