import torch
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTextEdit, QLabel, QMessageBox, QApplication)
from PyQt5.QtGui import QIcon
from models.DS_bot import DS_Bot
from models.simple_bot import SimpleBot
from ui.custom_widgets import MessageInput

class ChatTab(QWidget):
    def __init__(self, parent=None, api_key="", title="新对话", use_advanced=True):
        """Individual chat tab"""
        super().__init__(parent)
        self.title = title
        self.api_key = api_key
        self.bot = None
        self.use_advanced = use_advanced

        # Create bot instance
        if use_advanced and api_key:
            try:
                self.bot = DS_Bot(api_key=self.api_key)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"初始化高级机器人时出错: {str(e)}")
                self.bot = SimpleBot()
        else:
            self.bot = SimpleBot()

        # Create UI
        self.init_ui()

    def init_ui(self):
        """Initialize chat UI"""
        layout = QVBoxLayout()

        # Status indicator
        status_layout = QHBoxLayout()
        if self.use_advanced:
            status_label = QLabel("高级模式 ✓")
            status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            status_label = QLabel("简易模式 ⚠")
            status_label.setStyleSheet("color: orange; font-weight: bold;")
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Chat history area
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setAcceptRichText(True)
        self.chat_history.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")
        layout.addWidget(self.chat_history)

        # Input area
        input_layout = QHBoxLayout()
        # Use custom MessageInput class and pass self as parent
        self.message_input = MessageInput(self)
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet("border-radius: 5px;")
        input_layout.addWidget(self.message_input, 4)

        # Send button
        send_button = QPushButton("发送")
        send_button.setMinimumHeight(40)
        send_button.clicked.connect(self.send_message)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        input_layout.addWidget(send_button, 1)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        # Add welcome message
        if not self.use_advanced:
            self.chat_history.append(
                "<b>系统提示:</b> 您正在使用简易模式。如需使用高级功能，请确保提供有效的API密钥并安装GPU支持。")

    def send_message(self):
        """Send message and get reply"""
        if not self.bot:
            QMessageBox.warning(self, "错误", "机器人未初始化")
            return

        message = self.message_input.toPlainText().strip()
        if not message:
            return

        # Display user message
        self.chat_history.append(f"<div style='text-align: right;'><b>您:</b> {message}</div>")
        self.message_input.clear()

        # Get and display bot reply
        self.chat_history.append("<b>机器人:</b> <i>思考中...</i>")
        QApplication.processEvents()  # Update UI

        try:
            if isinstance(self.bot, DS_Bot):
                response = self.bot.get_response(message)
            else:
                response = self.bot.get_response(message)

            # Update the last line, remove "thinking..." and add reply
            cursor = self.chat_history.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()  # Delete extra newline
            self.chat_history.append(f"<b>机器人:</b> {response}")

        except Exception as e:
            self.chat_history.append(f"<b>错误:</b> {str(e)}")

        # Scroll to bottom
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum())

    def update_api_key(self, api_key, use_advanced=True):
        """Update API key and mode"""
        self.api_key = api_key
        self.use_advanced = use_advanced

        try:
            if use_advanced and api_key:
                self.bot = DS_Bot(api_key=self.api_key)
            else:
                self.bot = SimpleBot()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"更新机器人时出错: {str(e)}")
            self.bot = SimpleBot()

    def add_system_message(self, message):
        """Add a system message to the chat history"""
        self.chat_history.append(f"<b>系统提示:</b> {message}")
        # Scroll to bottom
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum())