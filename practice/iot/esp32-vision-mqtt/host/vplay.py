#! /usr/local/bin/python
# http://localhost:9090/a.mjpg
# python vplay.py -v output.mp4 -s 20   #  每0.2秒一畫面，( 0.01秒 x 20 )

import cv2
from http.server import CGIHTTPRequestHandler,HTTPServer
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', "--video",  help="file path")
parser.add_argument('-s', "--speed",  default=0 , type=int,  help="播放速度: 每多少厘秒(centisecond,百分之一秒)一畫面")  # frame / ( 0.01 second * speed )
args = parser.parse_args()

capture=None

class CamHandler(CGIHTTPRequestHandler):
    def do_GET(self):
        global capture
        print ( self.path )
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            sleeps = args.speed * 0.01
            try:
                while True:
                    rc,frame = capture.read()
                    if not rc:
                        if args.video :  capture = cv2.VideoCapture(args.video)
                        continue
                    r, buf = cv2.imencode(".jpg",frame)
                    self.wfile.write(b"--jpgboundary\r\n")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(len(buf)))
                    self.end_headers()
                    self.wfile.write(bytearray(buf))
                    self.wfile.write(b'\r\n')
                    time.sleep( sleeps )
            except KeyboardInterrupt:
                print('End server : 鍵盤 Ctrl-C 中斷')
                raise SystemExit
            except Exception as e:
                print( f'End server : Exception, {e}' )
                raise SystemExit
            except SystemExit as e:
                print( f'End server : SystemExit, {e}' )
                raise
            except :
                print('End server : Some Error')
                raise SystemExit
            finally:
                print( '網站伺服器結束⌛' )

def main():
    global capture
    if args.video :
        capture = cv2.VideoCapture(args.video)
    else:
        capture = cv2.VideoCapture(0)

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640); 
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);

    try:
        server = HTTPServer(('',9090),CamHandler)
        print( "server started 請用瀏覽器看我👀" )
        server.serve_forever()
    except KeyboardInterrupt:
        print('End program : 鍵盤 Ctrl-C 中斷')
    except Exception as e:
        print( f'End program : Exception, {e}' )
    except SystemExit as e:
        print(f'End program : SystemExit, {e}' )
    except :
        print('End program : Some Error')
    finally:
        capture.release()
        server.socket.close()
        print( '程式結束' )

if __name__ == '__main__':
    main()


#  https://github.com/berak/opencv_smallfry/blob/master/mjpg_serve.py

