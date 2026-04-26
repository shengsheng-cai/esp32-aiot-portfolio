import cv2
import time
from http.server import CGIHTTPRequestHandler, HTTPServer
import threading


def start_mjpg_server(port, get_frame, is_serving):
    """
    啟動 MJPEG HTTP 伺服器（背景 thread）。
    get_frame  : callable，回傳當前 frame (numpy array 或 None)
    is_serving : callable，回傳 bool，False 時結束串流
    回傳 HTTPServer 實例（呼叫端 finally 需 server.socket.close()）
    """
    class _Handler(CGIHTTPRequestHandler):
        def do_GET(self):
            if self.path.endswith('.mjpg'):
                self.send_response(200)
                self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
                self.end_headers()
                while is_serving():
                    frame = get_frame()
                    if frame is None:
                        time.sleep(0.1)
                        continue
                    r, buf = cv2.imencode('.jpg', frame)
                    self.wfile.write(b'--jpgboundary\r\n')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(buf)))
                    self.end_headers()
                    self.wfile.write(bytearray(buf))
                    self.wfile.write(b'\r\n')
                print('網站伺服器結束')

        def log_message(self, fmt, *args):
            pass

    server = HTTPServer(('', port), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f'server started  http://localhost:{port}/a.mjpg')
    return server
