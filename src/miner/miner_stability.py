""" Keep the Miner running """
import os

import paramiko
from utils.events import global_event, trigger_global_event

CRYPTO_USER = os.getenv("CRYPTO_USER")
PRIVATE_KEY_FILE = os.getenv("PRIVATE_KEY_FILE")


@global_event("miner_offline")
async def _miner_unavailable(miner_ip):
    print(f"Restarting Miner {miner_ip}")
    private_key = paramiko.Ed25519Key.from_private_key_file(PRIVATE_KEY_FILE)
    # OR private_key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_FILE)
    # OR private_key = paramiko.DSSKey.from_private_key_file(PRIVATE_KEY_FILE)
    ssh_client = paramiko.SSHClient()

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"connecting to {miner_ip}")
    ssh_client.connect(hostname=miner_ip, username=CRYPTO_USER, pkey=private_key)

    try:
        cmd = "export PATH=/home/cronqj/bin:$PATH && mine"
        print(f"running cmd: '{cmd}'")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
        print(ssh_stdout.read(), ssh_stderr.read())
        trigger_global_event('miner_restarted', miner_ip)

    finally:
        ssh_client.close()
