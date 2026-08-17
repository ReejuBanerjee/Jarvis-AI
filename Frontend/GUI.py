from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, 
                             QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QIcon, QMovie, QPixmap, QColor, QFont
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
AssistantName = env_vars.get("AssistantName", "Jarvis")

# Define crucial system paths dynamically
current_dir = os.getcwd()
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"
old_chat_messages = ""

# --- Helper File Operations ---
def SetMicrophoneStatus(Command):
    try:
        with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
            file.write(Command)
    except Exception as e:
        print(f"Error setting mic status: {e}")

def GetMicrophoneStatus():
    try:
        with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "False"

def GetAssistantStatus():
    try:
        with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
            val = file.read().strip()
            return val if val else "ONLINE & AVAILABLE"
    except FileNotFoundError:
        return "ONLINE & AVAILABLE"

def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'

# --- MISSING FUNCTIONS ADDED HERE FOR MAIN.PY ---
def SetAssistantStatus(status):
    try:
        with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
            file.write(status)
    except Exception as e:
        print(f"Error setting status: {e}")

def ShowTextToScreen(Text):
    try:
        with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
            file.write(Text)
    except Exception as e:
        print(f"Error writing to screen: {e}")

def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'

def AnswerModifier(Answer):
    return str(Answer)

def QueryModifier(Query):
    return str(Query)


# --- UI Screens ---
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        # Top Futuristic Subheading
        self.sub_label = QLabel(f"SYSTEM // {AssistantName.upper()} NEURAL CORE", self)
        self.sub_label.setStyleSheet("color: #4a6984; font-size: 13px; font-weight: 700; letter-spacing: 3px;")
        self.sub_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sub_label)

        # Central Assistant Orb (FIXED: Set to 16:9 ratio so the circle isn't squeezed)
        self.graphic_label = QLabel(self)
        self.graphic_label.setAlignment(Qt.AlignCenter)
        self.graphic_label.setFixedSize(800, 450)  # 16:9 widescreen ratio
        
        gif_path = GraphicsDirectoryPath("Jarvis.gif")
        jpg_path = GraphicsDirectoryPath("Jarvis.jpg")
        
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(800, 450)) # 16:9 widescreen ratio
            self.graphic_label.setMovie(self.movie)
            self.movie.start()
        elif os.path.exists(jpg_path):
            pixmap = QPixmap(jpg_path)
            self.graphic_label.setPixmap(pixmap.scaled(800, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        layout.addWidget(self.graphic_label, alignment=Qt.AlignCenter)

        # Assistant Status Text with Glow Effect
        self.label = QLabel("INITIALIZING...", self)
        self.label.setStyleSheet("""
            QLabel {
                color: #00e5ff;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 2px;
                background-color: transparent;
            }
        """)
        self.label.setAlignment(Qt.AlignCenter)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor("#00e5ff"))
        shadow.setOffset(0, 0)
        self.label.setGraphicsEffect(shadow)
        
        layout.addWidget(self.label)

        # Live status updater
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(300)
        
    def update_status(self):
        raw_status = GetAssistantStatus().upper()
        self.label.setText(raw_status)


class ChatSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # Chat Header
        header = QLabel(f"// {AssistantName.upper()} CONVERSATION LOGS", self)
        header.setStyleSheet("color: #00e5ff; font-size: 15px; font-weight: bold; letter-spacing: 2px; margin-bottom: 10px;")
        layout.addWidget(header)

        # Terminal-style output chat area
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #0a0e14;
                color: #00ffcc;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 15px;
                border: 1px solid #162436;
                border-radius: 12px;
                padding: 20px;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                border: none;
                background: #0a0e14;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #162436;
                min-height: 20px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.chat_area)
        
        # Live Chat Updater
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_chat)
        self.timer.start(500)
        
    def update_chat(self):
        global old_chat_messages
        try:
            with open(rf'{TempDirPath}\Responses.data', "r", encoding='utf-8') as file:
                new_chat = file.read()
            
            if new_chat != old_chat_messages and new_chat.strip():
                self.chat_area.append(f"\n{new_chat}")
                old_chat_messages = new_chat
        except Exception:
            pass


# --- Main Application Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dragPos = None
        
        # Frameless Dark Mode Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #040608;")

        # Master Layout Construction
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Left Sidebar Navigation
        sidebar = QFrame()
        sidebar.setFixedWidth(80)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #080c10;
                border-right: 1px solid #141c24;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 30, 10, 30)
        sidebar_layout.setSpacing(25)
        
        self.btn_home = self.create_icon_button("Home.png", 50)
        self.btn_chat = self.create_icon_button("Chats.png", 50)
        self.btn_settings = self.create_icon_button("Settings.png", 50)
        
        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_chat)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # 2. Main Content Body
        content_frame = QWidget()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 15, 20, 20)
        
        # Top Title Bar (Window Controls)
        title_bar = QHBoxLayout()
        title_bar.addStretch()
        
        # FIXED: Added the `is_titlebar` flag to give them a white backdrop!
        self.btn_min = self.create_icon_button("Minimize2.png", 32, is_titlebar=True)
        self.btn_max = self.create_icon_button("Maximize.png", 32, is_titlebar=True)
        self.btn_close = self.create_icon_button("Close.png", 32, is_titlebar=True)
        
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_maximize)
        self.btn_close.clicked.connect(self.close)
        
        # Add spacing between the top right buttons
        title_bar.addWidget(self.btn_min)
        title_bar.addSpacing(10)
        title_bar.addWidget(self.btn_max)
        title_bar.addSpacing(10)
        title_bar.addWidget(self.btn_close)
        content_layout.addLayout(title_bar)
        
        # Dynamic Stacked Views (Pages)
        self.stacked_widget = QStackedWidget()
        self.initial_screen = InitialScreen()
        self.chat_screen = ChatSection()
        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.chat_screen)
        content_layout.addWidget(self.stacked_widget)
        
        # Bottom Microphone Controls
        mic_layout = QHBoxLayout()
        mic_layout.addStretch()
        
        self.btn_mic = QPushButton()
        self.btn_mic.setFixedSize(80, 80)
        self.btn_mic.setCursor(Qt.PointingHandCursor)
        self.btn_mic.setStyleSheet("background-color: transparent; border: none;")
        self.update_mic_icon("Mic_off.png")
        self.btn_mic.clicked.connect(self.toggle_mic)
        
        mic_layout.addWidget(self.btn_mic)
        mic_layout.addStretch()
        content_layout.addLayout(mic_layout)
        
        main_layout.addWidget(content_frame)
        
        # Page Routing Connections
        self.btn_home.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_chat.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # Synchronize initial mic state
        SetMicrophoneStatus("False")
        
    # FIXED: Added logic for white backgrounds on black title bar icons
    def create_icon_button(self, icon_name, size, is_titlebar=False):
        btn = QPushButton()
        btn.setFixedSize(size, size)
        btn.setCursor(Qt.PointingHandCursor)
        icon_path = GraphicsDirectoryPath(icon_name)
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path))
            # Make the icon slightly smaller than the button so it sits inside the background nicely
            btn.setIconSize(QSize(size - 14, size - 14)) 
        
        if is_titlebar:
            # Title bar buttons get a solid light background so the black icons are visible
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #d1d5db;
                    border: none;
                    border-radius: {size // 2}px;
                }}
                QPushButton:hover {{
                    background-color: #ffffff;
                }}
            """)
        else:
            # Sidebar buttons remain transparent dark mode style
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #121b24;
                    border: 1px solid #1f2e3d;
                }
            """)
        return btn
        
    def update_mic_icon(self, icon_name):
        icon_path = GraphicsDirectoryPath(icon_name)
        if os.path.exists(icon_path):
            self.btn_mic.setIcon(QIcon(icon_path))
            self.btn_mic.setIconSize(QSize(70, 70))
            
    def toggle_mic(self):
        status = GetMicrophoneStatus()
        if status == "True":
            SetMicrophoneStatus("False")
            self.update_mic_icon("Mic_off.png")
        else:
            SetMicrophoneStatus("True")
            self.update_mic_icon("Mic_on.png")
            
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # Drag window handling with event propagation
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragPos:
            self.move(event.globalPos() - self.dragPos)
        super().mouseMoveEvent(event)

# --- Application Entry Point ---
def GraphicalUserInterface():
    os.makedirs(TempDirPath, exist_ok=True)
    for filename in ["Mic.data", "Status.data", "Responses.data"]:
        open(os.path.join(TempDirPath, filename), 'a').close()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()