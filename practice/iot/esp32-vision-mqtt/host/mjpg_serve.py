#! /usr/local/bin/python
# 課程示範原版（Python 2.7 tab-indent 轉換 → Python 3），保留作為對照
# 現代版請用 vplay.py（支援錄影檔、speed 參數、更完整的 error handling）
# http://raspberrypi.local:9090/a.mjpg   # 用來顯示 接在 rpi 的 camera
'''
	orig author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
	https://raw.githubusercontent.com/berak/opencv_smallfry/master/mjpg_serve.py        #  python 2.7
'''
import cv2
# from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer   # 原本的，只能用在 python 2.7 ，現在應該用 http.server
from http.server import BaseHTTPRequestHandler,HTTPServer
#from http.server import CGIHTTPRequestHandler,HTTPServer  # my test
import time

capture=None

class CamHandler(BaseHTTPRequestHandler):
#class CamHandler(CGIHTTPRequestHandler):  # my test
	def do_GET(self):
		print ( self.path )              # 原本 ( python 2.7 )：  print self.path   
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while True:
				try:
					rc,img = capture.read()
					if not rc:
						continue
#					imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
#					r, buf = cv2.imencode(".jpg",imgRGB)
					r, buf = cv2.imencode(".jpg",img)
					self.wfile.write(b"--jpgboundary\r\n")
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',str(len(buf)))
					self.end_headers()
					self.wfile.write(bytearray(buf))
					self.wfile.write(b'\r\n')
#					time.sleep(0.05)
				except KeyboardInterrupt:
					break
			return
		if self.path.endswith('.html') or self.path=="/":
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(b'<html><head></head><body>')
#			self.wfile.write(b'<img src="http://raspberrypi.local:9090/a.mjpg"/>')   # 用在 樹莓派
			self.wfile.write(b'<img src="http://127.0.0.1:9090/cam.mjpg"/>')         # 用在 桌機 筆電
			self.wfile.write(b'</body></html>')
			return

def main():
	global capture
	capture = cv2.VideoCapture(0)
	capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320); 
	capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);
	try:
		server = HTTPServer(('',9090),CamHandler)
		print( "server started" )           # 原本 ( python 2.7 )：  print "server started"
		server.serve_forever()
	except KeyboardInterrupt:
		capture.release()
		server.socket.close()

if __name__ == '__main__':
	main()


#  https://github.com/berak/opencv_smallfry/blob/master/mjpg_serve.py

