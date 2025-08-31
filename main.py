import asyncio
from itertools import islice
import socket
from typing import Any, Iterable, List, Tuple


class PortScan:

    MAX_CONCURRENT = 2000
    CHUNK_SIZE = 1000
    TIMEOUT = 1000

    def __init__(self, host: str, ports: List[int]) -> None:
        self.host = host
        self.ports = ports

    def _chunked(self, array: List[Any], size: int) -> Iterable[List[Any]]:

        it = iter(array)
        
        while True:
            chunk  = list(islice(it, size))
            
            if not chunk:
                break

            yield chunk

    async def _port_scan(self, port: int, semaphore: asyncio.Semaphore) -> Tuple[str, int] | None:
        loop = asyncio.get_running_loop()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)

        try:
            async with semaphore:
                await asyncio.wait_for(loop.sock_connect(sock, (self.host, port)), timeout=self.TIMEOUT)
                sock.close()

                return (self.host, port)        

        except:
            return None

    async def _handle_scan(self) -> None:
        semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)

        for port_chunk in self._chunked(self.ports, self.CHUNK_SIZE):

            tasks = [
                asyncio.create_task(self._port_scan(port, semaphore))
                for port in port_chunk
            ]

            for task in asyncio.as_completed(tasks):
                result = await task

                if result:
                    print(f"[+] {result[0]}:{result[1]}")

    def start(self) -> None:
        asyncio.run(self._handle_scan())


if __name__ == "__main__":
    PortScan("127.0.0.1", list(range(0, 65535))).start()
