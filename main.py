# main.py
from PyQt6.QtWidgets import QApplication
from app import ImageConverterApp

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    main_window = ImageConverterApp()
    main_window.show()
    sys.exit(app.exec())