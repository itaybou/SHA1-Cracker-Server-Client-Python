import socket, ipaddress, sys
import protocol
import queue as q
from time import sleep
import threading as threads
import io_handler as io
import packet_handler as handler


class UDPClient:
    RESPONSE_WAIT = 1
    TIMEOUT = 500
    BROADCAST_IP = '255.255.255.255'
    PORT = 3117

    def __init__(self):
        self.running = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.ip = socket.gethostbyname(socket.gethostname())
        self.active_servers = q.Queue()
        self.server_responses = q.Queue()
        self.lock = threads.Condition()
        self.receiver, self.responder = threads.Thread(target=self.fetch), threads.Thread(target=self.send)

    def start(self):
        self.client_socket.bind((self.ip, 0))  # A random free port from 1024 to 65535 will be selected
        self.run_client()
        return

    def run_client(self):
        try:
            hash_str, str_len = io.get_user_input()
            request = handler.create_request(hash_str, str_len)
            self.broadcast(request)
            self.running = True
            self.receiver.start(), self.responder.start()
            sleep(self.RESPONSE_WAIT)
            server_count = self.active_servers.qsize()
            if server_count == 0:
                io.print_error('Could not find active servers.')
                self.terminate()
            else:
                str_ranges = handler.divide_to_equal_ranges(str_len, server_count)
                for i in range(0, len(str_ranges)):
                    message = handler.create_request_with_ranges(hash_str, str_len, str_ranges[i])
                    address = self.active_servers.get(False)
                    self.active_servers.put(address)
                    self.client_socket.sendto(message, address)
        except ValueError as e:
            io.print_error(str(e))
            self.run_client()

    def fetch(self):
        while self.running:
            try:
                self.client_socket.settimeout(self.TIMEOUT)
                response = self.client_socket.recvfrom(protocol.BUFFER_SIZE)
                data, address = response
                if address is not None:
                    self.server_responses.put(response)
                self.lock.acquire()
                try:
                    self.lock.notifyAll()
                finally:
                    self.lock.release()
            except socket.timeout:
                if self.active_servers.qsize() != 0 and self.running:
                    self.active_servers.get(False)
                elif self.running:
                    self.terminate()
            except BlockingIOError:
                if self.running:
                    self.terminate()
        return

    def send(self):
        get_items = True
        while self.running:
            self.lock.acquire()
            try:
                while self.server_responses.empty() and self.running:
                    self.lock.wait()
                if not self.running:
                    get_items = False
            finally:
                self.lock.release()
            try:
                data, address = self.server_responses.get(get_items)
                handler.handle_response(data, address, self)
            except q.Empty:
                pass
        return

    def broadcast(self, request):
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  # allow reuse of ports
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # allow broadcast
        self.client_socket.sendto(request, (self.BROADCAST_IP, self.PORT))
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)  # cancel broadcast

    def clear_responses(self):
        while self.server_responses.qsize() != 0:
            self.server_responses.get(False)

    def terminate(self):
        try:
            self.running = False
            self.lock.acquire()
            try:
                self.lock.notify()
            finally:
                self.lock.release()
            self.client_socket.settimeout(0)
            self.client_socket.shutdown(socket.SHUT_RD)
            self.receiver.join(), self.responder.join()
        except socket.error:
            io.print_error('Terminating.')
        sys.exit(0)

