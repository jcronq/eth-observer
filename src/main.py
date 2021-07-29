# from fastapi import FastAPI
# import uvicorn
import os

import asyncio

from utils.events import run
from miner.miner_interface import MinerInterface
from miner.miner_monitor import monitor_interface
import miner.miner_alert
import miner.miner_stability

# app = FastAPI()

eth_miner_ip = os.getenv("MINER_IP")
eth_miner_port = os.getenv("MINER_PORT")
my_miner = MinerInterface(f"{eth_miner_ip}:{eth_miner_port}")
miner_monitor = monitor_interface(my_miner)

if __name__ == "__main__":
    print("Starting up ETH Observer")
    # uvicorn.run("main:app", host="0.0.0.0", port=9090, log_level="info")
    asyncio.run(run())
