import json
import socket
import select

from datetime import datetime

from utils.logger import print_exception

class EthminerSocket:
    def __init__(self):
        self.ip = None
        self.port = None
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connected = False

    def connect(self, ip, port):
        self.ip = ip
        self.port = port
        print('connecting', self.ip, self.port)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.ip, self.port))
        self.__connected = True

    def close(self):
        self.__socket.close()
        self.__connected = False

    def closed_unexpectedly(self):
        self.__connected = False
        raise RuntimeError("Socket connection broken")

    def send(self, data):
        if isinstance(data, str):
            data_str = data
        else:
            data_str = json.dumps(data)
        print(f"{self.ip}:{self.port}", data_str)
        data_bytes = f'{data_str}\n'.encode('utf-8')
        self.__socket.sendall(data_bytes)
    
    def receive(self):
        try:
            self.__socket.setblocking(0)
            msg = ""
            readable, writeable, exceptional = select.select([self.__socket], [], [], 1.0)
            if not (readable, writeable, exceptional):
                self.closed_unexpectedly()
            while len(msg) == 0 or msg[-1] != "\n":
                chunk = self.__socket.recv(2048)
                if chunk == b'':
                    self.closed_unexpectedly()
                msg += chunk.decode('utf-8')
            self.__socket.setblocking(1)
            return json.loads(msg[:-1])
        except BlockingIOError:
            self.closed_unexpectedly()


class MinerInterface:
    def __init__(self, address: str):
        self.__msg_id = 0

        [ip_str, port_str] = address.split(':')
        self.socket = EthminerSocket()
        self.ip = ip_str
        self.port = int(port_str)

    def __open_connection(self):
        self.socket.connect(self.ip, self.port)
    
    def __close_connection(self):
        self.socket.close()

    def __query_miner(self, query):
        additional_args = {
            "jsonrpc": "2.0",
            "id": self.__msg_id
        }
        ided_query = {**query, **additional_args}
        self.__open_connection()
        self.socket.send(ided_query)
        result = self.socket.receive()        
        self.__close_connection()
        return result
    
    @property
    def name(self):
        return self.ip.replace('.', '_')
    
    def ping(self):
        query = {
            "method": "miner_ping"
        }
        result = self.__query_miner(query)
        return result["result"]
    
    @property
    def status(self):
        query = {
            "method": "miner_getstatdetail"
        }
        result = self.__query_miner(query)
        return result["result"]
    
    @property
    def stat_1(self):
        query = {
            "method": "miner_getstat1"
        }
        result = self.__query_miner(query)
        return result["result"]

    def restart(self):
        query = {
            "method": "miner_restart"
        }
        result = self.__query_miner(query)
        return result["result"]

    def reboot(self):
        query = {
            "method": "miner_reboot"
        }
        result = self.__query_miner(query)
        return result["result"]

    def miner_shuffle(self):
        query = {
            "method": "miner_shuffle"
        }
        result = self.__query_miner(query)
        return result["result"]

    @property
    def connections(self):
        query = {
            "method": "miner_getconnections"
        }
        result = self.__query_miner(query)
        return result["result"]

    def set_active_connection_by_index(self, connection_index):
        query = {
            "method": "miner_setactiveconnection",
            "params": {
                "index": index
            }
        }
        result = self.__query_miner(query)
        return result["result"]

    def set_active_connection_by_uri(self, connection_uri):
        query = {
            "method": "miner_setactiveconnection",
            "params": {
                "URI": connection_uri
            }
        }
        result = self.__query_miner(query)
        return result["result"]

    def add_connection(self, connection_uri):
        query = {
            "method": "miner_addconnection",
            "params": {
                "uri": connection_uri
            }
        }
        result = self.__query_miner(query)
        return result["result"]

    def remove_connection(self, connection_index):
        query = {
            "method": "miner_removeconnection",
            "params": {
                "index": connection_index
            }
        }
        result = self.__query_miner(query)
        return result["result"]

    @property
    def scrambler_info(self):
        query = {
            "method": "miner_getscramblerinfo",
        }
        result = self.__query_miner(query)
        return result["result"]

    def set_scrambler_info(self, nonce_scrambler, segment_width):
        query = {
            "method": "miner_setscramblerinfo",
            "params": {
                "noncescrambler": nonce_scrambler,
                "segmentwidth": segment_width
            }
        }
        result = self.__query_miner(query)
        return result["result"]

    def pause_gpu(self, gpu_index):
        query = {
            "method": "miner_pausegpu",
            "params": {
                "index": gpu_index,
                "pause": True
            }
        }
        result = self.__query_miner(query)
        return result["result"]

    def unpause_gpu(self, gpu_index):
        query = {
            "method": "miner_pausegpu",
            "params": {
                "index": gpu_index,
                "pause": False
            }
        }
        result = self.__query_miner(query)
        return result["result"]
