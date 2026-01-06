import socket
from threading import Thread, Lock
from typing import List


class ServerSocket(Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True)  # 设置为守护线程
        self.HOST = host
        self.PORT = port
        self.clients: List[ClientServer] = []
        self.controller_stack = []
        self.lock = Lock()  # 线程锁保护共享数据

    def run(self):
        ss = socket.socket()
        ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许端口重用
        ss.bind((self.HOST, self.PORT))
        ss.listen(10)
        print("服务端已启动")

        while True:
            try:
                (socket_to_client, addr) = ss.accept()
                cs = ClientServer(socket_to_client, addr, self)
                cs.start()
            except Exception as e:
                print(f"接受连接时出错: {e}")

    def push(self, name: str):
        with self.lock:
            if name in [c.name for c in self.clients]:
                if (not self.controller_stack) or self.controller_stack[-1] != name:
                    self.controller_stack.append(name)

    def pop(self):
        with self.lock:
            if len(self.controller_stack) > 1:
                self.controller_stack.pop()
                if self.controller_stack[-1] not in [c.name for c in self.clients]:
                    self._pop_internal()  # 递归检查
            else:
                self.controller_stack.clear()

    def _pop_internal(self):
        """内部递归弹出（已持有锁）"""
        if len(self.controller_stack) > 1:
            self.controller_stack.pop()
            if self.controller_stack[-1] not in [c.name for c in self.clients]:
                self._pop_internal()
        else:
            self.controller_stack.clear()

    def top(self):
        with self.lock:
            controller_name = self.controller_stack[-1] if self.controller_stack else ' '
            for c in self.clients:
                c.try_send('change_controller ' + controller_name)


class ClientServer(Thread):
    def __init__(self, ss, addr, server):
        Thread.__init__(self, daemon=True)
        self.server = server
        self.socket = ss
        self.addr = addr
        self.type = 'unknown'
        self.name = ''
        self.controlling = False

    @property
    def clients(self):
        return self.server.clients

    @property
    def controller_stack(self):
        return self.server.controller_stack

    def read(self, size: int):
        buf = b''
        while len(buf) < size:
            data = self.socket.recv(size - len(buf))
            if not data:
                raise ConnectionError("连接已断开")
            buf += data
        return buf

    def readline(self, size: int = 32 * 1024):
        buf = b''
        while len(buf) < size:
            data = self.socket.recv(1)
            if not data:
                raise ConnectionError("连接已断开")
            buf += data
            if buf[-1] == 10:  # '\n'
                break
        buf = buf[:-1]
        return buf.decode('utf8')

    def run(self):
        try:
            self.handle()
        except ConnectionError as e:
            print(f"连接断开: {self.name or self.addr} - {e}")
        except Exception as e:
            print(f"处理客户端时出错: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        with self.server.lock:
            if self.controlling:
                self.server._pop_internal()
            if self in self.clients:
                self.clients.remove(self)
        self.get_list()
        try:
            self.socket.close()
        except:
            pass
        print("已关闭链接：" + (self.name or str(self.addr)))

    def handle(self):
        print('client connected', self.addr)

        firstLine = self.readline()
        if firstLine == "receiver":
            self.type = 'receiver'
            print("接收者接入")
        elif firstLine == "controller":
            self.type = 'controller'
            self.controlling = True
            print("控制者接入")
        else:
            self.socket.send(b'Who are you?\n')
            return

        self.name = self.readline()
        if not self.is_name_useable(self.name):
            self.try_send("duplicate_name")
            print("拒绝重名用户加入：", self.name)
            return
            
        print(self.name, "已加入会议")
        with self.server.lock:
            self.clients.append(self)
        self.get_list()

        while True:
            line = self.readline()
            print(self.addr, line)
            splits = line.split(' ')
            
            if splits[0] == 'command':
                if self.type == 'receiver' or not self.controlling:
                    continue
                self.send_to_receiver(line)
            elif splits[0] == 'exchange_control':
                self.exchange_control()
            elif splits[0] == 'switch_control':
                self.switch_control()
            elif splits[0] == 'ping':
                self.try_send('pong')
            else:
                print('Unknown message:', line)

    def get_list(self):
        with self.server.lock:
            member_list = 'member_list ' + ' '.join([c.name for c in self.clients])
            for c in self.clients:
                c.try_send(member_list)

    def is_name_useable(self, name):
        with self.server.lock:
            for c in self.clients:
                if c.name == name:
                    return False
            return True

    def exchange_control(self):
        with self.server.lock:
            if self.type == 'receiver':
                print("接收者入栈")
                self.server.push(self.name)
                for c in self.clients:
                    if c.type == 'controller':
                        c.type = 'receiver'
                self.type = 'controller'
                self.controlling = True
            elif self.type == 'controller':
                print("控制者出栈")
                self.server._pop_internal()
                self.type = 'receiver'
                self.controlling = False
                if self.controller_stack:
                    for c in self.clients:
                        if c.name == self.controller_stack[-1]:
                            c.type = 'controller'
                            c.controlling = True

        self.server.top()
        print(self.controller_stack)

    def switch_control(self):
        if self.type == 'controller':
            with self.server.lock:
                for c in self.clients:
                    c.try_send('control_switched ' + self.name)

    def send_to_receiver(self, msg: str):
        print("搜索并发送给接收者...")
        with self.server.lock:
            for c in self.clients:
                if c.type == 'receiver':
                    c.try_send(msg)

    def send(self, data):
        if type(data) == str:
            data = (data + '\n').encode('utf8')
        self.socket.send(data)

    def try_send(self, data):
        try:
            self.send(data)
        except Exception as e:
            print(f"尝试发送时发生错误: {e}")
