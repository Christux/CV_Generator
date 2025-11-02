import os
import time
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from functools import partial
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import websockets


class DevServer:

    def __init__(self, app_config, page_generator) -> None:
        self._app_config = app_config
        self._page_generator = page_generator
        self._rebuild_event = asyncio.Event()
        self._lock = threading.Lock()
        self._debounce_timer = None
        self._last_build_time = 0
        self._observer = None
        self._server_thread = None
        self._stop_event = threading.Event()
        self._loop = None

    def _rebuild(self):

        with self._lock:
            if self._debounce_timer:
                self._debounce_timer.cancel()

            self._debounce_timer = threading.Timer(0.2, self._do_rebuild)
            self._debounce_timer.daemon = True
            self._debounce_timer.start()

    def _do_rebuild(self):

        with self._lock:
            try:
                print("Rebuild in progress...")
                start = time.perf_counter()
                self._page_generator.build_page()
                elapsed = (time.perf_counter() - start) * 1000
                print(f"Build achieved in {elapsed:.1f} ms")
                self._last_build_time = time.time()
                if self._loop is not None:
                    asyncio.run_coroutine_threadsafe(
                        self._notify_reload(), self._loop)
            except Exception as e:
                print(f"Error in rebuild : {e}")

    async def _notify_reload(self):
        self._rebuild_event.set()

    def serve(self):
        # Watcher
        event_handler = ChangeHandler(self._rebuild)
        self._observer = Observer()
        for path in [
            self._app_config.config_file,
            self._app_config.data_file,
            self._app_config.abs_template_folder_path,
            self._app_config.abs_asset_folder_path,
        ]:
            if os.path.exists(path):
                self._observer.schedule(event_handler, path, recursive=True)
        self._observer.start()

        # Server HTTP
        handler = partial(SimpleHTTPRequestHandler,
                          directory=self._app_config.dist_folder)
        server = HTTPServer((self._app_config.server_host,
                            self._app_config.server_port), handler)
        self._server_thread = threading.Thread(
            target=server.serve_forever, daemon=True)
        self._server_thread.start()

        print(f"HTTP : http://{self._app_config.server_host}:{self._app_config.server_port}")
        print(f"WebSocket : ws://{self._app_config.server_host}:{self._app_config.server_websocket_port}")
        print(f"Watcher active on : {self._app_config.abs_template_folder_path}, {self._app_config.abs_asset_folder_path}")

        try:
            asyncio.run(self._ws_server())
        except KeyboardInterrupt:
            print("Stopping server...")
        finally:
            self._observer.stop()
            self._observer.join()
            server.shutdown()
            print("Server correctly stopped.")

    async def _ws_server(self):

        self._loop = asyncio.get_event_loop()

        async def handler(websocket):
            print(f"New client : {websocket.remote_address}")
            try:
                while not self._stop_event.is_set():
                    await self._rebuild_event.wait()
                    await asyncio.sleep(0.2)
                    await websocket.send("reload")
                    print("Reload sent to client.")
                    self._rebuild_event.clear()
            except Exception as e:
                print(f"Deconnexion of WebSocket : {e}")

        async with websockets.serve(handler, self._app_config.server_host, self._app_config.server_websocket_port):
            await asyncio.Future()


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, rebuild_callback):
        super().__init__()
        self.rebuild_callback = rebuild_callback

    def on_any_event(self, event):
        if not event.is_directory:
            if event.src_path.endswith(("~", ".swp", ".tmp")):
                return
            print(f"Change detected : {event.src_path}")
            self.rebuild_callback()
