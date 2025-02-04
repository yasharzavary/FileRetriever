from PySide6.QtWidgets import QApplication
import sys
from ui.ui import SearchEngineUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchEngineUI()
    window.show()
    sys.exit(app.exec())