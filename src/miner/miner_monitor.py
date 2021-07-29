from datetime import (
    datetime,
    timedelta
)
from utils.events import global_event, trigger_global_event

STATUS_OK = "OK"
STATUS_UNRESPONSIVE = "UNRESPONSIVE"

def monitor_interface(miner_interface):
    last_pong = None
    miner_state = None
    @global_event("on_update")
    async def _on_update():
        nonlocal last_pong
        nonlocal miner_state

        try:
            pong = miner_interface.ping()
            if pong == 'pong':
                now = datetime.utcnow()
                print('pong received', str(now))
                last_pong = now
                if miner_state == STATUS_UNRESPONSIVE or miner_state is None:
                    miner_state = STATUS_OK
                    trigger_global_event('miner_available', miner_interface.ip)
        except RuntimeError:
            print(f'miner at {miner_interface.name} is unreachable')
            miner_state = ping_failed(miner_interface.ip, last_pong, miner_state)
        except ConnectionRefusedError:
            print(f'miner at {miner_interface.name} is unreachable')
            miner_state = ping_failed(miner_interface.ip, last_pong, miner_state)

def ping_failed(miner_ip, last_pong, miner_state):
    now = datetime.utcnow()
    trigger_global_event('miner_offline', miner_ip)
    if (last_pong is None or last_pong + timedelta(minutes=1)) and (miner_state == STATUS_OK or miner_state == None):
        miner_state = STATUS_UNRESPONSIVE
        trigger_global_event('miner_unavailable', miner_ip)
    return miner_state
