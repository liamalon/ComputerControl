import datetime
import socket, threading, tcp_by_size
import sys
import os
import pyautogui   
from PIL import ImageGrab
import pygame
import mouse
from zlib import decompress


WIDTH = pyautogui.size().width - 100
HEIGHT = pyautogui.size().height - 100

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
        tcp_by_size.send_with_size(sock, data.encode())
    
    def recv_msg(self, sock):
        data = tcp_by_size.recv_by_size(sock).decode()
        code = data[:5]
        data = data[5:]
        return code, data

    def accept_clients(self):
        cli_sock,addr = self.sock.accept()
        print(f"connected, ip {addr}, port {self.port}")
        self.cli_sock = cli_sock
    
class ServerMouse(Server):
    def init_pos(self):
        self.prev_pos = None
        
    def check_movment(self):
        pos = mouse.get_position()
        if self.prev_pos == pos:
            return
        self.prev_pos = pos
        self.send_msg(self.cli_sock,"NEWP"+str(pos[0])+"-"+str(pos[1]))
    
    def check_pressed(self):
        clickd = pygame.mouse.get_pressed()
        btns = ["LEFT", "MIDDLE", "RIGHT"]
        for index, status in enumerate(clickd):
            if status == 1:
                self.send_msg(self.cli_sock, "CLIK"+btns[index])

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
    s_vid.start_server()
    s_vid.accept_clients()

    s_mouse = ServerMouse(4444)
    s_mouse.start_server()
    s_mouse.accept_clients()
    s_mouse.init_pos()

    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    watching = True

    while watching:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                break
        
        s_vid.get_screen()
        s_mouse.check_pressed()
        s_vid.show_screen(win)
        pygame.display.flip()
        clock.tick(60)