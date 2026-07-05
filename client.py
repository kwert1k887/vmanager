"""VMmanager API клиент."""

import requests
import urllib3
from typing import Optional

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VMClient:
    """Клиент для работы с VMmanager REST API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = False
        self._token: Optional[str] = None

    def authenticate(self, email: str, password: str) -> bool:
        """Получить токен авторизации."""
        resp = self.session.post(
            f"{self.base_url}/auth/v4/public/token",
            json={"email": email, "password": password},
        )
        if resp.status_code != 200:
            return False

        data = resp.json()
        self._token = data.get("token")
        if not self._token:
            return False

        self.session.headers.update({
            "x-xsrf-token": self._token,
            "Cookie": f"token={self._token}",
        })
        return True

    def _get(self, path: str) -> Optional[dict]:
        """GET-запрос к API."""
        resp = self.session.get(f"{self.base_url}/{path}")
        if resp.status_code != 200:
            return None
        try:
            return resp.json()
        except Exception:
            return None

    def _post(self, path: str, payload: dict) -> Optional[dict]:
        """POST-запрос к API."""
        resp = self.session.post(f"{self.base_url}/{path}", json=payload)
        if resp.status_code != 200:
            return None
        try:
            return resp.json()
        except Exception:
            return None

    def get_hostings(self) -> list:
        """Получить список виртуальных машин."""
        data = self._get("vm/v3/host")
        return data.get("list", []) if data else []

    def get_nodes(self) -> list:
        """Получить список узлов."""
        data = self._get("vm/v3/node")
        return data.get("list", []) if data else []

    def get_ips(self, limit: int = 50) -> list:
        """Получить список IP-адресов."""
        data = self._get(f"vm/v3/ip?limit={limit}")
        return data.get("list", []) if data else []

    def find_account(self, email: str) -> Optional[int]:
        """Найти аккаунт по email."""
        data = self._get(f"vm/v3/account?where=(email+EQ+'{email}')")
        if data and data.get("size", 0) > 0:
            return data["list"][0]["id"]
        return None

    def create_account(self, email: str) -> Optional[int]:
        """Создать новый аккаунт."""
        data = self._post("vm/v3/account", {
            "email": email,
            "password": "TempP@ssw0rd!",
            "role": "@user",
        })
        return data.get("id") if data else None

    def find_or_create_account(self, email: str) -> Optional[int]:
        """Найти или создать аккаунт."""
        account_id = self.find_account(email)
        if account_id:
            return account_id
        return self.create_account(email)

    def find_free_ip(self, node_id: int) -> Optional[str]:
        """Найти свободный IP на узле."""
        ips = self.get_ips()
        for ip in ips:
            if (
                ip.get("state", "").lower() == "free"
                and isinstance(ip.get("node"), dict)
                and ip["node"].get("id") == node_id
            ):
                return ip.get("ip")
        return None

    def get_node_cluster(self, node_id: int) -> Optional[int]:
        """Получить ID кластера узла."""
        nodes = self.get_nodes()
        for node in nodes:
            if node["id"] == node_id:
                return node.get("cluster")
        return None

    def create_vm(
        self,
        name: str,
        password: str,
        account_id: int,
        node_id: int,
        cluster_id: int,
        ip: str,
        cpu: int = 2,
        ram_mib: int = 2048,
        disk_mib: int = 20480,
        os_id: int = 13,
    ) -> Optional[int]:
        """Создать виртуальную машину."""
        data = self._post("vm/v3/host", {
            "name": name,
            "domain": f"{name}.example.com",
            "password": password,
            "cpu_number": cpu,
            "ram_mib": ram_mib,
            "disks": [{"size_mib": disk_mib, "boot_order": 1}],
            "os": os_id,
            "cluster": cluster_id,
            "account": account_id,
            "ip4": [{"ip": ip}],
            "node": node_id,
        })
        return data.get("id") if data else None
