# app.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from image_to_image import ImageToImageConverter
from image_to_pdf import ImageToPDFConverter

class ImageConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor de Imagem")
        self.setGeometry(100, 100, 800, 600)

        # Layout Principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Adiciona um espaçador acima do label
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Label
        self.label = QLabel("Escolha uma opção de conversão:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        self.layout.addWidget(self.label)

        # Layout dos Botões
        self.button_layout = QGridLayout()
        self.layout.addLayout(self.button_layout)

        # Botão de Imagem para Imagem
        self.image_to_image_button = QPushButton("Converter Imagem para Imagem")
        self.image_to_image_button.setIcon(QIcon("icons/image_to_image.png"))
        self.image_to_image_button.clicked.connect(self.open_image_to_image)
        self.button_layout.addWidget(self.image_to_image_button, 0, 0)

        # Botão de Imagem para PDF
        self.image_to_pdf_button = QPushButton("Converter Imagem para PDF")
        self.image_to_pdf_button.setIcon(QIcon("icons/image_to_pdf.png"))
        self.image_to_pdf_button.clicked.connect(self.open_image_to_pdf)
        self.button_layout.addWidget(self.image_to_pdf_button, 1, 0)

        # Adiciona um espaçador abaixo dos botões
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def open_image_to_image(self):
        self.hide()
        self.converter = ImageToImageConverter(self)
        self.converter.show()

    def open_image_to_pdf(self):
        self.hide()
        self.converter = ImageToPDFConverter(self)
        self.converter.show()
