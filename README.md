# 🖐️ Gesture Recognition - 手势识别会议控制系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8--3.10-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-1.9+-ee4c2c?logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/MediaPipe-0.8.9+-00A67E" alt="MediaPipe">
  <img src="https://img.shields.io/badge/PyQt5-5.15+-41CD52?logo=qt&logoColor=white" alt="PyQt5">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform">
</p>

基于 **MediaPipe** 手部检测和 **GRU 神经网络** 的实时手势识别系统，支持通过手势远程控制演示文稿、照片查看器等应用。

## ✨ 功能特性

- 🎥 **实时手势识别** - 通过摄像头实时检测和识别手势
- 🧠 **深度学习模型** - 使用 GRU 网络进行时序手势分类
- 🌐 **多人协作** - 支持控制者/被控者模式，可局域网协作
- 🖱️ **自动控制** - 自动模拟键盘鼠标操作
- 📱 **跨平台** - 支持 Windows、macOS、Linux

## 🎯 支持的手势

| 手势 | 功能 | 说明 |
|:----:|------|------|
| 👆 点击 | 鼠标左键点击 | 单指点击 |
| 👉 平移 | 切换下一页 | 向右滑动 |
| 🤏 缩放 | 缩小视图 | 双指捏合 |
| 🖐️ 放大 | 放大视图 | 双指展开 |
| 🔄 旋转 | 旋转图片 | 双手旋转 |
| ✊ 抓取 | 获取/释放控制权 | 握拳 |
| 📸 截图 | 屏幕截图 | 特定手势 |

## 📦 安装

### 环境要求

- Python 3.8 - 3.10
- 摄像头
- Windows 10/11（完整功能）或 macOS/Linux（部分功能）

### 快速开始

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/Gesture-Recognition.git
cd Gesture-Recognition

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

### PyTorch 安装

如果 pip 安装 PyTorch 失败，可以手动安装：

```bash
# CPU 版本
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# CUDA 版本 (NVIDIA GPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 🚀 使用方法

1. **启动程序** - 运行 `python app.py`
2. **输入用户名** - 在界面中输入你的用户名
3. **加入会议** - 点击「加入会议」按钮
4. **开启识别** - 点击「开始识别」启动摄像头
5. **获取控制** - 点击「获取控制」成为控制者
6. **开始控制** - 点击「开始控制」激活手势指令

> 💡 勾选「主持人模式」可让本机接受控制指令

## 🏗️ 项目结构

```
Gesture-Recognition/
├── app.py              # 🚀 主程序入口
├── GRU.py              # 🧠 GRU 神经网络模型定义
├── model.pt            # 📊 预训练模型权重
├── process.py          # 🔍 手势识别处理逻辑
├── interface.py        # 🖥️ GUI 界面逻辑
├── ui.py               # 🎨 PyQt5 界面定义
├── client.py           # 📡 网络客户端
├── server.py           # 🌐 网络服务端
├── server_offline.py   # 📴 离线服务端
├── reaction.py         # ⚡ 手势响应（模拟键鼠）
├── videos/             # 📹 教程视频
├── requirements.txt    # 📋 依赖列表
└── README.md           # 📖 说明文档
```

## 🌐 网络模式

程序支持多种网络连接方式：

| 模式 | 说明 |
|------|------|
| 远程服务器 | 自动尝试连接远程服务器 |
| 局域网 | 在同一网络内协作 |
| 本机服务器 | 无网络时作为独立服务器运行 |

### 局域网使用

```bash
# 服务端（一台电脑）
python server.py

# 客户端（其他电脑）
# 修改 client.py 中的服务器 IP 后运行
python app.py
```

## 💻 平台兼容性

| 功能 | Windows | macOS | Linux |
|------|:-------:|:-----:|:-----:|
| 手势识别 | ✅ | ✅ | ✅ |
| 摄像头预览 | ✅ | ✅ | ✅ |
| 键鼠模拟 | ✅ | ⚠️ | ⚠️ |
| 窗口检测 | ✅ | ❌ | ❌ |

> ⚠️ macOS/Linux 需要授予辅助功能权限才能模拟键鼠

## 🔧 故障排除

<details>
<summary><b>摄像头无法打开</b></summary>

- 检查摄像头是否被其他程序占用
- macOS: 系统设置 → 隐私与安全性 → 摄像头 → 授予权限
- Linux: 检查 `/dev/video0` 权限

</details>

<details>
<summary><b>MediaPipe 安装失败</b></summary>

- 确保 Python 版本为 3.8-3.10
- Apple Silicon Mac: `pip install mediapipe-silicon`
- 或尝试: `pip install --upgrade mediapipe`

</details>

<details>
<summary><b>模型加载失败</b></summary>

- 确保 `model.pt` 文件存在于项目根目录
- 检查 PyTorch 版本是否兼容

</details>

<details>
<summary><b>网络连接失败</b></summary>

- 检查防火墙是否阻止了端口 12345
- 确认服务端已正常启动

</details>

## 🛠️ 技术栈

- **手部检测**: [MediaPipe](https://mediapipe.dev/)
- **深度学习**: [PyTorch](https://pytorch.org/)
- **GUI 框架**: [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- **计算机视觉**: [OpenCV](https://opencv.org/)
- **输入模拟**: pyuserinput (Windows) / pynput (macOS/Linux)

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

<p align="center">
  Made with ❤️ for gesture recognition
</p>
