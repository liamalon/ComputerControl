import pickle
import socket, threading, tcp_by_size
from time import sleep
import mss, pyautogui
from pynput import mouse 
from pynput import keyboard
from zlib import compress
import keyboard as keyboard_block


WIDTH = pyautogui.size().width - 50
HEIGHT = pyautogui.size().height - 50


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
    
    def recv_msg(self, sock, decoded = True):
        data = tcp_by_size.recv_by_size(sock)

        code = data[:4].decode()
        data = data[4:]

        if decoded:
            data = data.decode()
        return code, data

class ClientKeyBoard(Client):
    def start_threading(self):
        self.keyboard = keyboard.Controller()
        t = threading.Thread(target=self.handle_server)
        t.start()

    def handle_server(self):
        self.running = True
        while self.running:
            code, data = self.recv_msg(self.sock)
            state = ""
            match code:           
                case "KEYP":
                    state = "P"
                case "KEYR":
                    state = "R"
            self.press_key(state, data)
        
    def press_key(self, state, key):
        try:
            if state == "P":
                self.keyboard.press(key.replace("\'",""))
            else:
                self.keyboard.release(key.replace("\'",""))
        except:
            pass

class ClientMouse(Client):
    def start_threading(self):
        self.mouse = mouse.Controller()
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
                    meta_data = data.split("-")
                    self.click_mouse(meta_data[0], meta_data[1])
        
    def move_mouse(self, x, y):
        self.mouse.position = (x,y)

    def click_mouse(self, press_or_realse, btn):
        btns = {"left": mouse.Button.left, "right": mouse.Button.right, "middle": mouse.Button.middle}
        if press_or_realse =="P":
            self.mouse.press(btns[btn])
        else:
            self.mouse.release(btns[btn])

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

class BlockInputs():
    def __init__(self):
        self.block_input_flag = 1
        self.mouse_control = mouse.Controller()

    def block_inputs(self):
        t1 = threading.Thread(target=self.blockinput_start)
        t1.start()

        print("[SUCCESS] Input blocked!")

    def unblock_inputs(self):
        self.blockinput_stop()

        print("[SUCCESS] Input unblocked!")

    def blockinput_start(self):
        for i in range(150):
            keyboard_block.block_key(i)

        while self.block_input_flag == 1:
            self.mouse_control.position = (0, 0)

    def blockinput_stop(self):
        for i in range(150):
            keyboard_block.unblock_key(i)

        self.block_input_flag = 0

if __name__ == "__main__":
    c_v = ClientVideo(8888, "192.168.1.107")
    c_v.start_sending()

    c_m = ClientMouse(4444, "192.168.1.107")
    c_m.start_threading()

    c_k = ClientKeyBoard(2222, "192.168.1.107")
    c_k .start_threading()

    input_blocker = BlockInputs()
    input_blocker.block_inputs()
    sleep(10)
    input_blocker.unblock_inputs()

    while True:
        pass

        
        