import random
import socket, threading, tcp_by_size
import mss, pyautogui
import mouse
from zlib import compress

WIDTH = pyautogui.size().width - 100
HEIGHT = pyautogui.size().height - 100

class Client:
    def __init__(self, port, ip) -> None:
        self.port = port
        self.ip = ip
        self.sock = socket.socket()
        self.connect_to_server()
    
    def connect_to_server(self):
        self.sock.connect((self.ip, self.port))

    def send_msg(self, sock, data):
        tcp_by_size.send_with_size(sock, data.encode())
    
    def recv_msg(self, sock):
        data = tcp_by_size.recv_by_size(sock).decode()
        code = data[:5]
        data = data[5:]
        return code, data

class ClientMouse(Client):
    def start_threading(self):
        t = threading.Thread(target=self.handle_server)
        t.start()

    def handle_server(self):
        self.running = True
        while self.running:
            code, data = self.recv_msg(self.sock)
            match code:
                case "NEWP":
                    pos = data.split("-")
                    self.move_mouse(int(pos[0]), int(pos[1]))
                
                case "CLIK":
                    self.click_mouse(data)
        
    def move_mouse(self, x, y):
        mouse.move(x, y, absolute=True)

    def click_mouse(self, btn):
        mouse.click(button=btn)

class ClientVideo(Client):    
    def retreive_screenshot(self):
        with mss.mss() as sct:
            # The region to capture
            rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

            while 'recording':
                # Capture the screen
                img = sct.grab(rect)
                # Tweak the compression level here (0-9)
                pixels = compress(img.rgb, 6)

                # Send the size of the pixels length
                size = len(pixels)
                size_len = (size.bit_length() + 7) // 8
                self.sock.send(bytes([size_len]))

                # Send the actual pixels length
                size_bytes = size.to_bytes(size_len, 'big')
                self.sock.send(size_bytes)

                # Send pixels
                self.sock.sendall(pixels)
        
    def start_sending(self):
        t = threading.Thread (target = self.retreive_screenshot)
        t.start()


if __name__ == "__main__":
    c_v = ClientVideo(8888, "127.0.0.1")
    c_v.start_sending()

    c_m = ClientMouse(4444, "127.0.0.1")
    c_m.start_threading()

    while True:
        pass

        
        