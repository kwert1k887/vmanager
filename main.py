"""vmanager — CLI для управления виртуальными машинами через VMmanager API."""

import sys
from client import VMClient
from config import Config


def print_menu():
    print("\nВыберите действие:")
    print("1 — Список виртуальных машин")
    print("2 — Создать ВМ")
    print("3 — Список IP-адресов")
    print("0 — Выход")


def action_list_vms(client: VMClient):
    vms = client.get_hostings()
    if not vms:
        print("Нет доступных виртуальных машин.")
        return

    for idx, vm in enumerate(vms, 1):
        ips = ", ".join(ip.get("ip") for ip in vm.get("ip4", [])) or "нет IP"
        account = vm.get("account", {})
        print(f"\n--- ВМ #{idx} ---")
        print(f"  ID:     {vm.get('id')}")
        print(f"  Имя:    {vm.get('name')}")
        print(f"  ОС:     {vm.get('os_name')} ({vm.get('os_group')})")
        print(f"  Статус: {vm.get('state')}")
        print(f"  IP:     {ips}")
        print(f"  CPU:    {vm.get('cpu_number')} ядер")
        print(f"  RAM:    {vm.get('ram_mib')} MiB")
        print(f"  Диск:   {vm.get('total_disks_size_mib')} MiB")


def action_create_vm(client: VMClient):
    email = input("Email владельца: ").strip()
    if not email:
        print("Email не может быть пустым.")
        return

    account_id = client.find_or_create_account(email)
    if not account_id:
        print("Не удалось получить аккаунт.")
        return

    nodes = client.get_nodes()
    if not nodes:
        print("Нет доступных узлов.")
        return

    print("\nДоступные узлы:")
    for node in nodes:
        print(f"  ID: {node['id']}  Имя: {node.get('name')}")

    node_id = input("ID узла: ").strip()
    if not node_id.isdigit():
        print("Некорректный ID.")
        return
    node_id = int(node_id)

    free_ip = client.find_free_ip(node_id)
    if not free_ip:
        print("Нет свободных IP на выбранном узле.")
        return
    print(f"Свободный IP: {free_ip}")

    name = input("Имя ВМ: ").strip()
    password = input("Пароль root: ").strip()

    cluster_id = client.get_node_cluster(node_id)
    if not cluster_id:
        print("Не удалось получить кластер узла.")
        return

    vm_id = client.create_vm(
        name=name,
        password=password,
        account_id=account_id,
        node_id=node_id,
        cluster_id=cluster_id,
        ip=free_ip,
    )

    if vm_id:
        print(f"ВМ '{name}' создана. ID: {vm_id}")
    else:
        print("Ошибка при создании ВМ.")


def action_list_ips(client: VMClient):
    ips = client.get_ips()
    if not ips:
        print("Нет IP-адресов.")
        return

    for ip in ips:
        node = ip.get("node")
        node_id = node.get("id") if node else None
        vm = ip.get("vm")
        vm_name = vm.get("name") if vm else None
        print(f"  IP: {ip.get('ip')}  Node: {node_id}  Статус: {ip.get('state')}  VM: {vm_name or '—'}")


def main():
    config = Config()

    if not config.email or not config.password:
        print("Задайте VM_EMAIL и VM_PASSWORD в .env или переменных окружения.")
        sys.exit(1)

    client = VMClient(config.base_url)
    if not client.authenticate(config.email, config.password):
        print("Ошибка авторизации.")
        sys.exit(1)

    print("Авторизация успешна.")

    while True:
        print_menu()
        choice = input(">>> ").strip()

        if choice == "0":
            break
        elif choice == "1":
            action_list_vms(client)
        elif choice == "2":
            action_create_vm(client)
        elif choice == "3":
            action_list_ips(client)
        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()
