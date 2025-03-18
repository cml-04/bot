import re
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QLabel, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.username = ""
        self.api_key = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("登录")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Username field
        self.username_edit = QLineEdit()
        form_layout.addRow("用户名:", self.username_edit)

        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("注册")
        self.register_button.clicked.connect(self.register)

        self.forgot_button = QPushButton("忘记密码")
        self.forgot_button.clicked.connect(self.forgot_password)

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.forgot_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
            return

        user_data = self.db.verify_login(username, password)
        if user_data:
            self.username = username
            self.api_key = user_data.get("api_key", "")
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误")

    def register(self):
        register_dialog = RegisterDialog(self.db, self)
        if register_dialog.exec_() == QDialog.Accepted:
            self.username = register_dialog.username
            self.api_key = ""
            self.accept()

    def forgot_password(self):
        forgot_dialog = ForgotPasswordDialog(self.db, self)
        forgot_dialog.exec_()


class RegisterDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.username = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("注册账号")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Username field
        self.username_edit = QLineEdit()
        form_layout.addRow("用户名:", self.username_edit)

        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("密码:", self.password_edit)

        # Confirm password field
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("确认密码:", self.confirm_password_edit)

        # Security question field
        self.security_question_edit = QLineEdit()
        form_layout.addRow("安全问题:", self.security_question_edit)

        # Security answer field
        self.security_answer_edit = QLineEdit()
        form_layout.addRow("答案:", self.security_answer_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.register_button = QPushButton("注册")
        self.register_button.clicked.connect(self.register)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        security_question = self.security_question_edit.text().strip()
        security_answer = self.security_answer_edit.text().strip()

        # Validate input
        if not username or not password or not security_question or not security_answer:
            QMessageBox.warning(self, "输入错误", "所有字段都必须填写")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            return

        # Password strength check
        if len(password) < 6:
            QMessageBox.warning(self, "密码强度不足", "密码长度应至少为6个字符")
            return

        # Check if username already exists
        if self.db.user_exists(username):
            QMessageBox.warning(self, "注册失败", "用户名已被占用")
            return

        # Register the user
        if self.db.add_user(username, password, security_question, security_answer):
            QMessageBox.information(self, "注册成功", "账号已创建，请登录")
            self.username = username
            self.accept()
        else:
            QMessageBox.warning(self, "注册失败", "无法创建账号，请重试")


class ForgotPasswordDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("找回密码")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Username field
        self.username_edit = QLineEdit()
        form_layout.addRow("用户名:", self.username_edit)

        self.security_question_label = QLabel("请输入用户名并点击查询")
        form_layout.addRow("安全问题:", self.security_question_label)

        self.security_answer_edit = QLineEdit()
        form_layout.addRow("答案:", self.security_answer_edit)

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("新密码:", self.new_password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("确认新密码:", self.confirm_password_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.query_button = QPushButton("查询")
        self.query_button.clicked.connect(self.query_security_question)

        self.reset_button = QPushButton("重置密码")
        self.reset_button.clicked.connect(self.reset_password)
        self.reset_button.setEnabled(False)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.query_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def query_security_question(self):
        username = self.username_edit.text().strip()

        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            return

        security_question = self.db.get_security_question(username)

        if security_question:
            self.security_question_label.setText(security_question)
            self.reset_button.setEnabled(True)
        else:
            self.security_question_label.setText("未找到该用户")
            self.reset_button.setEnabled(False)

    def reset_password(self):
        username = self.username_edit.text().strip()
        answer = self.security_answer_edit.text().strip()
        new_password = self.new_password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()

        if not username or not answer or not new_password:
            QMessageBox.warning(self, "输入错误", "所有字段必须填写")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            return

        # Password strength check
        if len(new_password) < 6:
            QMessageBox.warning(self, "密码强度不足", "密码长度应至少为6个字符")
            return

        # Reset the password
        if self.db.reset_password(username, answer, new_password):
            QMessageBox.information(self, "密码重置成功", "您的密码已重置，请用新密码登录")
            self.accept()
        else:
            QMessageBox.warning(self, "密码重置失败", "安全问题答案错误或用户不存在")