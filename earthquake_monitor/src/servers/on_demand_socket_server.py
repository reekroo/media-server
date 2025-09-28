import asyncio
import os
import json
import logging
from dataclasses import asdict

from services.on_demand_earthquake_service import OnDemandEarthquakeService

class OnDemandSocketServer:
    def __init__(self, socket_path: str, service: OnDemandEarthquakeService, logger: logging.Logger):
        self._socket_path = socket_path
        self._service = service
        self._log = logger
        self._server = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client_addr = writer.get_extra_info('peername')
        self._log.info(f"On-demand server: New connection from {client_addr}")
        
        try:
            request_data_bytes = await reader.read(1024)
            if not request_data_bytes:
                return

            request_data = request_data_bytes.decode('utf-8')
            self._log.info(f"On-demand server: Received request: {request_data}")
            request = json.loads(request_data)

            lat = request.get("lat")
            lon = request.get("lon")
            days = request.get("days", 1)

            if lat is None or lon is None:
                raise ValueError("'lat' or 'lon' key is missing in request")

            events = await self._service.get_earthquakes_for_coords(
                lat=float(lat), lon=float(lon), days=int(days)
            )

            events_as_dict = [asdict(event) for event in events]
            response = {"status": "success", "data": events_as_dict}
            
            writer.write(json.dumps(response).encode('utf-8'))
            await writer.drain()
            self._log.info(f"On-demand server: Sent {len(events)} events for coords ({lat}, {lon}).")

        except (json.JSONDecodeError, ValueError) as e:
            self._log.error(f"On-demand server: Invalid request from client: {e}")
            error_response = {"status": "error", "message": "Invalid JSON request. 'lat' and 'lon' are required."}
            writer.write(json.dumps(error_response).encode('utf-8'))
            await writer.drain()
        except Exception as e:
            self._log.error(f"On-demand server: Error handling client: {e}", exc_info=True)
        finally:
            self._log.info(f"On-demand server: Closing connection from {client_addr}")
            writer.close()
            await writer.wait_closed()

    async def start(self):
        if os.path.exists(self._socket_path):
            os.remove(self._socket_path)
            
        self._server = await asyncio.start_unix_server(
            self.handle_client,
            path=self._socket_path
        )
        
        os.chmod(self._socket_path, 0o666)
        
        addr = self._server.sockets[0].getsockname()
        self._log.info(f"On-demand earthquake socket server listening on {addr}")
        
        async with self._server:
            await self._server.serve_forever()

    async def stop(self):
        self._log.info("Stopping On-demand earthquake server...")
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        
        if os.path.exists(self._socket_path):
            try:
                await asyncio.to_thread(os.remove, self._socket_path)
            except OSError as e:
                self._log.error(f"Error removing socket file: {e}")