from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTabWidget,
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon


class BotSelector(QWidget):
    """Bot selection panel with vertical tabs"""

    # Define signals properly at class level
    bot_changed = pyqtSignal(str)  # Signal emitted when bot type changes
    collapse_requested = pyqtSignal(bool)  # Signal for collapse/expand

    def __init__(self, parent=None, use_advanced=False):
        super().__init__(parent)
        self.parent = parent
        self.use_advanced = use_advanced
        self.current_bot_type = "simple" if not use_advanced else "advanced"
        self.is_collapsed = False

        self.init_ui()

    def init_ui(self):
        """Initialize the bot selector UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Header with title and collapse button
        header_layout = QHBoxLayout()

        # Title
        select_label = QLabel("选择机器人")
        select_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(select_label)

        # Collapse/expand button
        self.collapse_btn = QPushButton()
        self.collapse_btn.setIcon(QIcon("icons/collapse.png"))
        self.collapse_btn.setToolTip("折叠面板")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        header_layout.addWidget(self.collapse_btn)

        layout.addLayout(header_layout)

        # Bot selection tabs (vertical)
        self.bot_tabs = QTabWidget()
        self.bot_tabs.setTabPosition(QTabWidget.West)  # Tabs on left side

        # Simple bot tab
        simple_bot_widget = QWidget()
        simple_bot_layout = QVBoxLayout(simple_bot_widget)
        simple_bot_info = QLabel("简易机器人\n\n• 本地运行\n• 无需API\n• 基础对话功能")
        simple_bot_info.setWordWrap(True)
        simple_bot_layout.addWidget(simple_bot_info)
        simple_bot_layout.addStretch()
        self.bot_tabs.addTab(simple_bot_widget, QIcon("icons/simple_bot.png"), "简易")

        # Advanced bot tab
        ds_bot_widget = QWidget()
        ds_bot_layout = QVBoxLayout(ds_bot_widget)
        ds_bot_info = QLabel("高级AI\n\n• DeepSeek AI\n• 需要API密钥\n• 高级对话理解\n• 图像生成")
        ds_bot_info.setWordWrap(True)
        ds_bot_layout.addWidget(ds_bot_info)
        ds_bot_layout.addStretch()
        self.bot_tabs.addTab(ds_bot_widget, QIcon("icons/advanced_bot.png"), "高级")

        # Connect bot selection signal
        self.bot_tabs.currentChanged.connect(self.change_bot_type)

        layout.addWidget(self.bot_tabs)

        # API settings button
        self.api_btn = QPushButton("API设置")
        self.api_btn.clicked.connect(self.request_api_settings)
        layout.addWidget(self.api_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Select appropriate tab based on available features
        self.bot_tabs.setCurrentIndex(1 if self.use_advanced else 0)

    def toggle_collapse(self):
        """Toggle sidebar collapse/expand state"""
        self.is_collapsed = not self.is_collapsed

        if self.is_collapsed:
            self.collapse_btn.setIcon(QIcon("icons/expand.png"))
            self.collapse_btn.setToolTip("展开面板")
            self.bot_tabs.setVisible(False)
            self.api_btn.setVisible(False)
        else:
            self.collapse_btn.setIcon(QIcon("icons/collapse.png"))
            self.collapse_btn.setToolTip("折叠面板")
            self.bot_tabs.setVisible(True)
            self.api_btn.setVisible(True)

        # Emit signal to notify parent to adjust splitter sizes
        self.collapse_requested.emit(self.is_collapsed)

    def change_bot_type(self, index):
        """Change the bot type based on tab selection"""
        print(f"触发切换，索引: {index}")
        self.bot_changed.emit(self.current_bot_type)
        self.current_bot_type = "advanced" if index == 1 else "simple"

        # If advanced selected but not available, show warning
        if self.current_bot_type == "advanced" and not self.use_advanced:
            QMessageBox.warning(
                self,
                "功能受限",
                "高级模式需要API密钥和GPU支持。请在设置中配置API密钥。"
            )

        # Emit signal to notify parent
        self.bot_changed.emit(self.current_bot_type)

    def request_api_settings(self):
        """Request to show API settings dialog from parent"""
        if self.parent and hasattr(self.parent, 'show_api_settings'):
            self.parent.show_api_settings()

    def update_status(self, use_advanced):
        """Update bot selector status when API settings change"""
        self.use_advanced = use_advanced

        # If current bot is advanced but advanced mode is not available, switch to simple
        if self.current_bot_type == "advanced" and not use_advanced:
            self.bot_tabs.setCurrentIndex(0)
            self.current_bot_type = "simple"
            self.bot_changed.emit(self.current_bot_type)