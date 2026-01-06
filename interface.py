import time
import cv2

from PyQt5 import QtGui
from PyQt5.QtCore import QStringListModel, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from ui import Ui_MainWindow
from threading import Event
from reaction import Reaction
from tutorialsWin import TutorialsWin
from helpWin import HelpWin


class Window(QMainWindow, Ui_MainWindow):
    received = pyqtSignal(str)

    def __init__(self, app, parent=None):
        super(Window, self).__init__(parent)
        self.app = app
        self.setupUi(self)
        self.btn_start.clicked.connect(self.switch)
        self.eventRunning = Event()

        self.member_list = []
        self._list_view_connected = False  # 防止重复绑定信号

        self.received.connect(self.get_data)
        self.isLogin = False
        self.isTarget = False
        self.isController = False
        self.isControlling = False
        self.btn_get_ctrl.clicked.connect(self.get_ctrl)
        self.type = 'receiver'
        self.name = ''
        self.target = ''
        self.btn_join.clicked.connect(self.join)
        self.btn_pause.clicked.connect(self.switch_ctrl)
        self.checkBox.stateChanged.connect(self.switch_target)

        self.reaction = Reaction()
        self.action_tutorials.triggered.connect(self.show_tutorials_win)
        self.action_help.triggered.connect(self.show_help_win)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """窗口关闭事件，清理资源"""
        # 停止识别线程
        self.eventRunning.clear()
        self.app.identify.break_loop()
        # 停止网络
        self.app.client.stop_ping()
        a0.accept()

    def join(self):
        self.name = self.lineEdit.text()
        if self.name != '':
            self.app.client.send(self.name)  # 发送用户名
            self.btn_join.setEnabled(False)
            self.lineEdit.setEnabled(False)
            self.btn_join.setText("已加入会议")
            self.isLogin = True
            self.app.identify.start()
        else:
            self.show_error("请输入用户名")
            self.lineEdit.setFocus()

    def get_ctrl(self):
        if self.isLogin:
            if self.isController:
                self.app.client.send("exchange_control")
                self.btn_get_ctrl.setText("获取控制")
                self.btn_pause.setText("开始控制")
            else:
                self.app.client.send("exchange_control")
                self.isController = True
                self.btn_get_ctrl.setText("退出控制")
                self.btn_pause.setText("开始控制")
        else:
            self.show_error("尚未加入会议")
            self.lineEdit.setFocus()

    def switch_ctrl(self):
        if self.isController:
            self.app.client.send("switch_control")
            self.btn_pause.setText("暂停控制" if self.btn_pause.text() == "开始控制" else "开始控制")
        else:
            self.show_error("未获得控制权")

    def switch_target(self):
        self.isTarget = self.checkBox.isChecked()

    def get_data(self, data: str):
        if data == 'pong':
            return
        elif data == 'ping':
            self.app.client.timer.start()
            return
        
        splits = data.split(' ')
        if not splits:
            return
            
        if splits[0] == 'command':
            if len(splits) > 1:
                self.set_log("控制者发出指令：" + splits[1])
                if self.isTarget:
                    self.reaction.react(splits[1])

        elif splits[0] == 'change_controller':
            self.isControlling = False
            controller_name = splits[1] if len(splits) > 1 else ''
            self.label_controller.setText(
                ("正在控制：" if self.isControlling else "控制已暂停：") + controller_name
            )
            if controller_name == self.name:
                self.isController = True
                self.btn_get_ctrl.setText("退出控制")
            else:
                self.isController = False
                self.btn_get_ctrl.setText("获取控制")
                
        elif splits[0] == 'control_switched':
            self.isControlling = not self.isControlling
            controller_name = splits[1] if len(splits) > 1 else ''
            self.label_controller.setText(
                ("正在控制：" if self.isControlling else "控制已暂停：") + controller_name
            )
            
        elif splits[0] == 'member_list':
            self.member_list = splits[1:]
            self.init_list_view()
            
        elif splits[0] == 'duplicate_name':
            self.show_error("用户名已存在，请修改")
            self.lineEdit.setEnabled(True)
            self.lineEdit.setFocus()
            self.btn_join.setEnabled(True)
            self.btn_join.setText("加入会议")
            self.isLogin = False

    def set_gesture(self, msg: str):
        self.label_res.setText(msg)
        if msg == "抓取":
            if not self.isController:
                self.get_ctrl()
                self.switch_ctrl()
            else:
                self.switch_ctrl()
                self.get_ctrl()
            return
            
        if self.isControlling:
            if self.isTarget:
                self.textBrowser.append("控制本机：" + msg)
                self.reaction.react(msg)
                return
            if self.isController:
                self.set_log("你发出了指令：" + msg)
                self.app.client.send("command " + msg)
                return

    def set_log(self, msg):
        self.textBrowser.append(time.strftime("(%H:%M:%S)", time.localtime()) + ' ' + msg)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)

    def flash_img(self, image, ratio):
        """更新摄像头画面"""
        try:
            if image is None:
                return
            size = (int(self.label_img.width()), int(self.label_img.width() * ratio))
            if size[0] <= 0 or size[1] <= 0:
                return
            shrink = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
            shrink = cv2.cvtColor(shrink, cv2.COLOR_BGR2RGB)
            self.QtImg = QtGui.QImage(
                shrink.data, shrink.shape[1], shrink.shape[0], 
                shrink.shape[1] * 3, QtGui.QImage.Format_RGB888
            )
            self.label_img.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
        except Exception as e:
            print(f"更新画面失败: {e}")

    def switch(self):
        if self.eventRunning.isSet():
            self.label_img.setText("Hello\nWorld")
            self.btn_start.setText("开启识别")
            self.eventRunning.clear()
        else:
            self.eventRunning.set()
            self.btn_start.setText("停止识别")

    def show_error(self, msg: str):
        QMessageBox.information(self, "错误", msg)

    def init_list_view(self):
        slm = QStringListModel()
        slm.setStringList(self.member_list)
        self.listView.setModel(slm)
        # 只绑定一次信号，避免重复绑定
        if not self._list_view_connected:
            self.listView.clicked.connect(self.clicked_list)
            self._list_view_connected = True

    def clicked_list(self, q_model_index):
        if 0 <= q_model_index.row() < len(self.member_list):
            self.target = self.member_list[q_model_index.row()]

    def show_tutorials_win(self):
        self.switch()
        TutorialsWin().exec_()

    def show_help_win(self):
        HelpWin().exec_()
