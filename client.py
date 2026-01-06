import socket
import threading
import time

from server_offline import ServerSocket


class Client:
    def __init__(self, app):
        self.app = app
        self.type = 'receiver'
        self.client = None
        self.host = socket.gethostbyname(socket.gethostname())
        self.pingTimes = 0
        self.isPing = True
        self.pingInterval = 60
        self.timer = threading.Timer(self.pingInterval, self.send_ping)
        self.connected = False

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def create_socket(self):
        """创建新的 socket 对象"""
        if self.client:
            try:
                self.client.close()
            except:
                pass
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5)  # 设置超时时间

    def run(self):
        max_retries = 3
        
        # 尝试连接远程服务器
        print("尝试连接远程服务器...")
        for i in range(max_retries):
            try:
                self.create_socket()
                self.client.connect(('zhude.guet.ltd', 12345))
                print("远程服务器已连接")
                self.connected = True
                self.send(self.type)
                break
            except Exception as e:
                print(f"连接远程服务器失败 ({i+1}/{max_retries}): {e}")
                time.sleep(1)
        
        # 如果远程连接失败，尝试局域网
        if not self.connected:
            print("尝试连接局域网服务器...")
            for i in range(max_retries):
                try:
                    self.create_socket()
                    self.client.connect((self.host, 12345))
                    print("局域网服务器已连接")
                    self.connected = True
                    self.send(self.type)
                    break
                except Exception as e:
                    print(f"连接局域网失败 ({i+1}/{max_retries}): {e}")
                    time.sleep(1)
        
        # 如果都失败，启动本地服务器
        if not self.connected:
            print("正在启动本机服务端...")
            self.start_server()
            time.sleep(1)  # 等待服务器启动
            
            for i in range(max_retries):
                try:
                    self.create_socket()
                    self.client.connect((self.host, 12345))
                    print("已连接到本机服务端")
                    self.connected = True
                    self.send(self.type)
                    break
                except Exception as e:
                    print(f"连接本机服务端失败 ({i+1}/{max_retries}): {e}")
                    time.sleep(1)
        
        if not self.connected:
            print("无法建立连接，请检查网络设置")
            return
        
        # 设置为阻塞模式用于接收数据
        self.client.settimeout(None)
        
        try:
            while self.connected:
                if self.app.win.type == 'receiver':
                    try:
                        data = self.readline()
                        if data:
                            self.app.win.received.emit(data)
                    except Exception as e:
                        print(f"接收数据出错: {e}")
                        break
        except Exception as e:
            print(f"连接异常: {e}")
        finally:
            self.connected = False
            if self.client:
                try:
                    self.client.close()
                except:
                    pass

    def readline(self, size: int = 32 * 1024):
        buf = b''
        while len(buf) < size:
            try:
                recv = self.client.recv(1)
                if len(recv) == 0:
                    raise Exception("连接已断开")
                buf += recv
                if buf[-1] == 10:
                    break
            except socket.timeout:
                continue
            except Exception as e:
                raise e
        buf = buf[:-1]
        return buf.decode('utf8')

    def send(self, data):
        if not self.connected and self.client is None:
            return
        try:
            if type(data) == str:
                data = (data + '\n').encode('utf8')
            self.client.send(data)
        except Exception as e:
            print(f"发送数据失败: {e}")

    def start_server(self):
        server = ServerSocket(self.host, 12345)
        server.start()

    def send_ping(self):
        if self.isPing and self.connected:
            print('ping')
            self.send('ping')
            self.timer = threading.Timer(self.pingInterval, self.send_ping)
            self.timer.start()

    def stop_ping(self):
        self.isPing = False
        if self.timer:
            self.timer.cancel()
