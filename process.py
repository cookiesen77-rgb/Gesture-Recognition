import threading
import cv2
import time
import platform
import os
from GRU import *
import torch
import mediapipe as mp
import numpy as np


class Identify:
    def __init__(self, win):
        self.win = win
        self.isEnd = False
        self.cap = None

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def init_camera(self):
        """初始化摄像头，返回是否成功"""
        print("正在初始化摄像头...")
        
        # 尝试不同的摄像头索引和后端
        backends = []
        
        if platform.system() == 'Windows':
            backends = [
                (0, cv2.CAP_DSHOW),
                (0, cv2.CAP_MSMF),
                (0, cv2.CAP_ANY),
            ]
        elif platform.system() == 'Darwin':  # macOS
            backends = [
                (0, cv2.CAP_AVFOUNDATION),
                (0, cv2.CAP_ANY),
                (1, cv2.CAP_ANY),
            ]
        else:  # Linux
            backends = [
                (0, cv2.CAP_V4L2),
                (0, cv2.CAP_ANY),
                ('/dev/video0', cv2.CAP_ANY),
            ]
        
        for camera_id, backend in backends:
            try:
                print(f"尝试打开摄像头: {camera_id}, 后端: {backend}")
                self.cap = cv2.VideoCapture(camera_id, backend)
                
                if self.cap.isOpened():
                    # 尝试读取一帧来验证
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        print(f"摄像头初始化成功！分辨率: {frame.shape[1]}x{frame.shape[0]}")
                        return True
                    else:
                        self.cap.release()
                        print("摄像头打开但无法读取帧")
                else:
                    print("摄像头无法打开")
                    
            except Exception as e:
                print(f"尝试失败: {e}")
                if self.cap:
                    self.cap.release()
        
        print("所有摄像头初始化尝试均失败")
        return False

    def run(self):
        # 初始化摄像头
        if not self.init_camera():
            print("错误：无法打开摄像头！")
            print("请检查：")
            print("  1. 摄像头是否已连接")
            print("  2. 是否已授予摄像头权限")
            print("  3. 摄像头是否被其他程序占用")
            return
        
        movement = {0: "点击", 1: "平移", 2: "缩放", 3: "抓取", 4: "旋转", 5: "无", 6: "截图", 7: '放大'}
        S = 0  # 每帧的处理时间
        device = torch.device('cpu')  # 初始化于cpu上处理
        
        if torch.cuda.is_available():
            device = torch.device('cuda:0')
            print("使用 CUDA 加速")
        else:
            print("使用 CPU 模式")

        # 加载模型
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'model.pt')
            model = torch.load(model_path, map_location='cpu').to(device)
            print("模型加载成功")
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.cap.release()
            return
        
        hiddem_dim = 30  # 隐藏层大小
        num_layers = 2  # GRU层数

        h_t = torch.zeros(num_layers, 1, hiddem_dim)
        h_t = h_t.to(device)

        last_gesture = '无'
        prin_time = time.time()

        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        
        # 获取高宽比，添加安全检查
        width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if width > 0 and height > 0:
            ratio = height / width
        else:
            ratio = 0.75  # 默认 4:3 比例
        
        print(f"摄像头分辨率: {int(width)}x{int(height)}")

        try:
            with mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.65,
                    min_tracking_confidence=0.5) as hands:
                
                start_time = time.time()
                frame_count = 0
                fps_time = time.time()

                while self.cap.isOpened():
                    if self.isEnd:
                        break
                    
                    self.win.eventRunning.wait()

                    in_dim = torch.zeros(126)

                    wait_time = S - (time.time() - start_time)
                    if wait_time > 0:
                        time.sleep(wait_time)
                    start_time = time.time()

                    success, image = self.cap.read()
                    if not success or image is None:
                        print("无法读取摄像头帧")
                        time.sleep(0.1)
                        continue
                    
                    # 计算 FPS
                    frame_count += 1
                    if time.time() - fps_time >= 1.0:
                        # print(f"FPS: {frame_count}")
                        frame_count = 0
                        fps_time = time.time()

                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

                    image.flags.writeable = False
                    results = hands.process(image)

                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    if results.multi_hand_landmarks:
                        if len(results.multi_handedness) == 1 and results.multi_handedness[0].classification.__getitem__(0).index == 1:
                            for hand_landmarks in results.multi_hand_landmarks:
                                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                                index_1 = []
                                for k in range(0, 21):
                                    index_1.append(hand_landmarks.landmark[k].x)
                                    index_1.append(hand_landmarks.landmark[k].y)
                                    index_1.append(hand_landmarks.landmark[k].z)
                                for k_1 in range(0, 63):
                                    index_1.append(0)
                            in_dim = torch.from_numpy(np.array(index_1))
                            
                        elif len(results.multi_handedness) == 1 and results.multi_handedness[0].classification.__getitem__(0).index == 0:
                            for hand_landmarks in results.multi_hand_landmarks:
                                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                                index_0 = []
                                for k_1 in range(0, 63):
                                    index_0.append(0)
                                for k in range(0, 21):
                                    index_0.append(hand_landmarks.landmark[k].x)
                                    index_0.append(hand_landmarks.landmark[k].y)
                                    index_0.append(hand_landmarks.landmark[k].z)
                            in_dim = torch.from_numpy(np.array(index_0))
                            
                        elif len(results.multi_handedness) == 2 and results.multi_handedness[0].classification.__getitem__(0).index == 1:
                            index_1_first = []
                            for hand_landmarks in results.multi_hand_landmarks:
                                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                                for k in range(0, 21):
                                    index_1_first.append(hand_landmarks.landmark[k].x)
                                    index_1_first.append(hand_landmarks.landmark[k].y)
                                    index_1_first.append(hand_landmarks.landmark[k].z)
                            in_dim = torch.from_numpy(np.array(index_1_first))
                            
                        elif len(results.multi_handedness) == 2 and results.multi_handedness[0].classification.__getitem__(0).index == 0:
                            results.multi_hand_landmarks.reverse()
                            index_0_first = []
                            for hand_landmarks in results.multi_hand_landmarks:
                                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                                for k in range(0, 21):
                                    index_0_first.append(hand_landmarks.landmark[k].x)
                                    index_0_first.append(hand_landmarks.landmark[k].y)
                                    index_0_first.append(hand_landmarks.landmark[k].z)
                            in_dim = torch.from_numpy(np.array(index_0_first))

                    if self.win.eventRunning.isSet():
                        self.win.flash_img(image, ratio)

                    in_dim = in_dim.unsqueeze(dim=0)
                    in_dim = in_dim.unsqueeze(dim=0)
                    in_dim = in_dim.to(torch.float32).to(device)
                    h_t = h_t.to(torch.float32).to(device)
                    
                    if time.time() - prin_time < 2:
                        in_dim = torch.zeros(1, 1, 126).to(device)

                    rel, h_t = model((in_dim, h_t))
                    rel = torch.sigmoid(rel)
                    confidence, rel = rel.max(1)

                    cfd = {'点击': 0.90, '平移': 0.90, '缩放': 0.99, '抓取': 0.985, '旋转': 0.99, '无': 0, '截图': 0.99, '放大': 0.9}
                    if confidence > cfd[movement[rel.item()]]:
                        now_gesture = last_gesture
                        last_gesture = movement[rel.item()]
                        if not (now_gesture == last_gesture):
                            if time.time() - prin_time > 2:
                                self.win.set_gesture(movement[rel.item()])
                                prin_time = time.time()
                                h_t = torch.zeros(num_layers, 1, hiddem_dim).to(device)
                                
        except Exception as e:
            print(f"运行时错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.cap:
                self.cap.release()
            print("摄像头已释放")

    def break_loop(self):
        self.isEnd = True
