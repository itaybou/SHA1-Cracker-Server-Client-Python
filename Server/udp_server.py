import socket
import protocol
import threading as threads
import queue as q
import packet_handler as handler
from pebble import pool
from functools import partial
from concurrent.futures import TimeoutError


class UDPServer:
    TIMEOUT = 700
    MAX_CLIENTS = 10
    GENERAL_IP = '0.0.0.0'
    PORT = 3117

    def __init__(self):
        self.running = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.pool = pool.process.ProcessPool(self.MAX_CLIENTS)
        self.messages = q.Queue()
        self.lock = threads.Condition()
        self.receiver, self.responder = threads.Thread(target=self.fetch), threads.Thread(target=self.send)

    def start(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            self.server_socket.bind((self.GENERAL_IP, self.PORT))
            self.running = True
            self.receiver.start(), self.responder.start()
            print("UDP Server started.")
        except OSError:
            print("Server already open on this machine.")
        return

    def fetch(self):
        while self.running:
            data, address = self.server_socket.recvfrom(protocol.BUFFER_SIZE)
            task = self.pool.schedule(handler.handle_packet, args=(data, address), timeout=self.TIMEOUT)
            task.add_done_callback(partial(self.add_message, address))
        return

    def send(self):
        while self.running:
            self.lock.acquire()
            try:
                while self.messages.empty():
                    self.lock.wait()
            finally:
                self.lock.release()
            data, address = self.messages.get()
            self.server_socket.sendto(data, address)
            print("Packet of type {} sent to address {}:{}.".format(data[protocol.MSG_TYPE_INDEX], address[0], address[1]))
        return

    def add_message(self, address, addressed_message_future):
        try:
            self.messages.put(addressed_message_future.result())
        except TimeoutError:
            print("Request from {}:{} timed out! (Server timeout: {}sec)".format(address[0], address[1], self.TIMEOUT))
            self.messages.put(handler.add_nack_message(address))
        self.lock.acquire()
        try:
            self.lock.notify()
        finally:
            self.lock.release()
