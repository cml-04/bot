import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import ChatBotUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use modern style

    window = ChatBotUI()
    window.show()

    sys.exit(app.exec_())