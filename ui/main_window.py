import os
import sys
import torch
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QTabWidget, QSplitter,
                           QMessageBox, QInputDialog, QLineEdit, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from models.database import UserDatabase
from ui.chat_tab import ChatTab
from ui.auth_dialogs import LoginDialog
from ui.bot_selector import BotSelector


class ChatBotUI(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Initialize database
        self.db = UserDatabase("chatbot.db")

        # User info
        self.username = ""
        self.api_key = ""
        self.use_advanced = False
        self.current_bot_type = "simple"

        # Login first
        self.check_login()

        # Initialize UI
        self.init_ui()

    def check_login(self):
        """Check if user is logged in"""
        login_dialog = LoginDialog(self.db)

        if login_dialog.exec_():
            self.username = login_dialog.username
            self.api_key = login_dialog.api_key
            self.check_requirements()
        else:
            # User canceled login
            sys.exit()

    def check_requirements(self):
        """Check advanced mode requirements"""
        gpu_available = torch.cuda.is_available()
        api_valid = bool(self.api_key)

        self.use_advanced = gpu_available and api_valid

        if not self.use_advanced:
            warnings = []
            if not gpu_available:
                warnings.append("- 未检测到GPU支持")
            if not api_valid:
                warnings.append("- 未设置API密钥")

            self.needs_api_setup = not api_valid

    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle(f"AI聊天助手 - {self.username}")
        self.setGeometry(100, 100, 900, 600)

        # Set application icon
        self.setWindowIcon(QIcon("icons/chat_icon.png"))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create a splitter for left sidebar and main content
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # Store original sizes for collapse/expand
        self.sidebar_width = 200

        # Left sidebar with bot selector
        self.bot_selector = BotSelector(self, self.use_advanced)
        self.bot_selector.bot_changed.connect(self.on_bot_type_changed)
        self.bot_selector.collapse_requested.connect(self.toggle_sidebar)
        self.splitter.addWidget(self.bot_selector)

        # Right content area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Chat tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        right_layout.addWidget(self.tab_widget)

        # Bottom buttons
        button_layout = QHBoxLayout()

        # New chat button
        new_chat_btn = QPushButton("新对话")
        new_chat_btn.clicked.connect(self.create_new_chat)
        new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        button_layout.addWidget(new_chat_btn)

        button_layout.addStretch()

        # User info
        user_info = QLabel(f"用户: {self.username}")
        button_layout.addWidget(user_info)

        # Logout button
        logout_btn = QPushButton("注销")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #607d8b;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #455a64;
            }
        """)
        button_layout.addWidget(logout_btn)

        right_layout.addLayout(button_layout)

        # Add widgets to splitter
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([self.sidebar_width, 700])  # Set initial sizes

        # Create initial chat
        self.current_bot_type = "simple" if not self.use_advanced else "advanced"
        self.create_new_chat()

        # Prompt for API setup if needed
        if hasattr(self, 'needs_api_setup') and self.needs_api_setup:
            QTimer.singleShot(100, self.prompt_api_settings)

    def on_bot_type_changed(self, bot_type):
        """Handle bot type change from selector"""
        print(f"目前是{bot_type}模式，高级模式可用性: {self.use_advanced}")
        self.current_bot_type = bot_type

        # Apply change to current active chat tab
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            current_tab = self.tab_widget.widget(current_index)

            # Use the selected bot type but respect advanced mode availability
            use_advanced = self.current_bot_type == "advanced" and self.use_advanced

            # Update tab icon
            icon = QIcon("icons/advanced_bot.png" if use_advanced else "icons/simple_bot.png")
            self.tab_widget.setTabIcon(current_index, icon)

            # Update the chat tab's bot
            current_tab.update_api_key(self.api_key, use_advanced)

            # Add system message about bot change
            bot_type_name = "高级" if use_advanced else "简易"
            current_tab.add_system_message(f"已切换到{bot_type_name}模式")

    def create_new_chat(self):
        """Create a new chat tab"""
        count = self.tab_widget.count()

        # Use the currently selected bot type
        use_advanced = self.current_bot_type == "advanced" and self.use_advanced

        chat_tab = ChatTab(
            parent=self,
            api_key=self.api_key,
            title=f"对话 {count + 1}",
            use_advanced=use_advanced
        )

        # Set tab icon based on bot type
        icon = QIcon("icons/advanced_bot.png" if use_advanced else "icons/simple_bot.png")

        self.tab_widget.addTab(chat_tab, icon, f"对话 {count + 1}")
        self.tab_widget.setCurrentIndex(count)

    def close_tab(self, index):
        """Close a chat tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.information(self, "提示", "至少需要保留一个对话")

    def show_api_settings(self):
        """Show API settings dialog"""
        api_key, ok = QInputDialog.getText(
            self, "API设置",
            "请输入Deepseek API密钥:",
            QLineEdit.Normal,
            self.api_key
        )

        if ok:
            self.api_key = api_key.strip()

            # Update API key in database
            self.db.update_api_key(self.username, self.api_key)

            # Recheck requirements
            self.check_requirements()

            # Update bot selector
            self.bot_selector.update_status(self.use_advanced)

            # Update all tabs
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                tab.update_api_key(self.api_key, self.use_advanced)

            QMessageBox.information(self, "成功", "API设置已更新")

    def prompt_api_settings(self):
        """Prompt user to set API key"""
        response = QMessageBox.question(
            self,
            "设置API密钥",
            "您尚未设置Deepseek API密钥，是否现在设置？",
            QMessageBox.Yes | QMessageBox.No
        )

        if response == QMessageBox.Yes:
            self.show_api_settings()

    def logout(self):
        """Log out current user"""
        reply = QMessageBox.question(
            self, '确认注销',
            '确定要注销当前账号吗?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Restart application logic
            QApplication.quit()
            program = sys.executable
            os.execl(program, program, *sys.argv)

    def toggle_sidebar(self, collapsed):
        """Handle sidebar collapse/expand"""
        if collapsed:
            # Store current width before collapsing
            self.sidebar_width = self.splitter.sizes()[0]
            # Collapse sidebar (set to minimal width)
            self.splitter.setSizes([40, self.splitter.sizes()[1] + self.sidebar_width - 40])
        else:
            # Expand sidebar (restore previous width)
            current_sizes = self.splitter.sizes()
            self.splitter.setSizes([self.sidebar_width, current_sizes[1] - (self.sidebar_width - 40)])