
import socket, threading, tcp_by_size
from time import time
import pyautogui   
import pygame
from pynput import mouse, keyboard 
from zlib import decompress


WIDTH = pyautogui.size().width 
HEIGHT = pyautogui.size().height 

class Server:
    def __init__(self, port) -> None:
        self.port = port
        self.sock = socket.socket()
        self.cli_sock = None
        self.sockets_id = []
    
    def start_server(self):
        print("server")
        self.sock.bind(('0.0.0.0', self.port))
        self.sock.listen(20)
        print('after listen ... start accepting')
    
    def send_msg(self, sock, data):
        if type(data) != bytes:
            data = data.encode()
        tcp_by_size.send_with_size(sock, data)
    
    def recv_msg(self, sock):
        data = tcp_by_size.recv_by_size(sock).decode()
        code = data[:4]
        data = data[4:]
        return code, data

    def accept_clients(self):
        cli_sock,addr = self.sock.accept()
        print(f"connected, ip {addr}, port {self.port}")
        self.cli_sock = cli_sock
    
    def run(self):
        self.start_server()
        self.accept_clients()
    
class ServerMouse(Server):
    def __init__(self, port):
        super().__init__(port)
        self.start = time()

    def check_movment(self, x, y):
        if time() - self.start > 0.03:
            pos = (x, y)
            if self.prev_pos == pos:
                return
            self.prev_pos = pos
            self.send_msg(self.cli_sock,"NEWP"+str(x)+"-"+str(y))
            self.start = time()

    def start_listener(self):
        self.prev_pos = None
        listener_movment = mouse.Listener(on_move=self.check_movment)
        listener_movment.start()

        listener_pressed = mouse.Listener(on_click=self.check_pressed)
        listener_pressed.start()
    
    def check_pressed(self, x, y, button, pressed):
        if pressed:
            self.send_msg(self.cli_sock,"CLIK" + "P-"+ str(button).split(".")[1])
        else:
            self.send_msg(self.cli_sock,"CLIK" + "R-"+ str(button).split(".")[1])
    
    def run(self):
        self.start_server()
        self.accept_clients()
        self.start_listener()

class ServerKeyBoard(Server):
    def start_listener(self):
        listener_movment = keyboard.Listener(on_press = self.check_pressed, on_release=self.check_released)
        listener_movment.start()
    
    def check_pressed(self, key):
        self.send_msg(self.cli_sock, "KEYP"+str(key))

    def check_released(self, key):
        self.send_msg(self.cli_sock, "KEYR"+str(key))
    
    def run(self):
        self.start_server()
        self.accept_clients()
        self.start_listener()
        
class ServerVideo(Server):
    def recvall(self, conn, length):
        """ Retreive all pixels. """
        buf = b''
        while len(buf) < length:
            data = conn.recv(length - len(buf))
            if not data:
                return data
            buf += data
        return buf

    def get_screen(self):
        # Retreive the size of the pixels length, the pixels length and pixels
        size_len = int.from_bytes(self.cli_sock.recv(1), byteorder='big')
        size = int.from_bytes(self.cli_sock.recv(size_len), byteorder='big')
        pixels = decompress(self.recvall(self.cli_sock, size))
        # Create the Surface from raw pixels
        self.img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

    def show_screen(self, win):
        win.blit(self.img, (0, 0))

if __name__ == "__main__":

    s_vid = ServerVideo(8888)
    s_vid.run()

    s_mouse = ServerMouse(4444)
    s_mouse.run()

    s_keyboard = ServerKeyBoard(2222)
    s_keyboard.run()

        
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True

    while watching:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                break
        
        s_vid.get_screen()
        s_vid.show_screen(win)
        pygame.display.flip()
        clock.tick(60)