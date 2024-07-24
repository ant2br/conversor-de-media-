from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox, QSizePolicy,
    QScrollArea, QGridLayout, QProgressBar, QSpacerItem
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QImage, QPixmap

class ImageToImageConverter(QWidget):
    def __init__(self, parent_app):
        super().__init__()

        self.parent_app = parent_app
        self.image_paths = []

        self.init_ui()
        self.worker = None

    def init_ui(self):
        self.setWindowTitle("Converter Imagem para Imagem")
        self.setGeometry(100, 100, 800, 600)  # Tamanho da janela

        # Layout principal
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Espaçador
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Label
        self.label = QLabel("Selecione imagens para converter")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 15px;")
        self.layout.addWidget(self.label)

        # Espaçador
        self.layout.addItem(QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Botão de Seleção
        self.select_button = QPushButton("Selecionar Imagens")
        self.select_button.clicked.connect(self.select_images)
        self.select_button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px; 
                padding: 12px; 
                border-radius: 8px;
            }
            """
        )
        self.layout.addWidget(self.select_button)

        # Espaçador
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Formato de Entrada
        self.input_format_label = QLabel("Formato de Entrada:")
        self.input_format_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.input_format_label)

        self.input_format = QComboBox()
        self.input_format.addItems(["PNG", "JPEG", "BMP", "GIF", "TIFF"])
        self.input_format.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.input_format)

        # Formato de Saída
        self.output_format_label = QLabel("Formato de Saída:")
        self.output_format_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.output_format_label)

        self.output_format = QComboBox()
        self.output_format.addItems(["JPEG", "PNG"])
        self.output_format.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.output_format)

        # Área de Pré-visualização
        self.preview_label = QLabel("Pré-visualização das Imagens:")
        self.preview_label.setStyleSheet("font-size: 16px;")
        self.layout.addWidget(self.preview_label)

        # Container para o layout de imagens
        self.preview_container = QWidget()
        self.preview_layout = QGridLayout(self.preview_container)
        self.preview_container.setLayout(self.preview_layout)
        
        # Área de rolagem para o layout de imagens
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.preview_container)
        self.layout.addWidget(self.scroll_area)

        # Barra de Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximum(100)
        self.layout.addWidget(self.progress_bar)

        # Botão de Conversão
        self.convert_button = QPushButton("Converter")
        self.convert_button.clicked.connect(self.convert_images)
        self.convert_button.setEnabled(False)
        self.convert_button.setStyleSheet(
            """
            QPushButton {
                font-size: 18px; 
                padding: 12px; 
                border-radius: 8px;
            }
            """
        )
        self.layout.addWidget(self.convert_button)

        # Espaçador
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Botão de Voltar
        self.back_button = QPushButton("Voltar ao Menu")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px; 
                padding: 12px; 
                border-radius: 8px;
            }
            """
        )
        self.layout.addWidget(self.back_button)

    def select_images(self):
        new_image_paths, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar Imagens", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"
        )
        if new_image_paths:
            self.image_paths.extend(new_image_paths)
            self.preview_images()
            self.label.setText(f"{len(self.image_paths)} imagem(s) selecionada(s).")
            self.convert_button.setEnabled(True)

    def preview_images(self):
        # Remover todos os widgets do layout
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Definir o tamanho máximo para o Pixmap
        max_size = 300

        # Adicionar as imagens ao layout de grade
        row = 0
        col = 0
        total_height = 0
        num_images = len(self.image_paths)
        
        for path in self.image_paths:
            try:
                # Cria um QLabel para a imagem
                image_label = QLabel()
                img = QImage(path)
                
                if img.isNull():
                    print(f"Imagem não carregada: {path}")
                    continue

                # Calcula o tamanho do Pixmap mantendo a proporção
                original_size = img.size()
                if original_size.width() > original_size.height():
                    scaled_size = QSize(max_size, max_size * original_size.height() // original_size.width())
                else:
                    scaled_size = QSize(max_size * original_size.width() // original_size.height(), max_size)

                pixmap = QPixmap.fromImage(img).scaled(scaled_size, Qt.AspectRatioMode.KeepAspectRatio)
                
                # Configura o QLabel com o QPixmap
                image_label.setPixmap(pixmap)
                image_label.setFixedSize(pixmap.size())  # Ajusta o tamanho do QLabel para o tamanho do Pixmap

                # Adiciona o QLabel ao layout de grade
                self.preview_layout.addWidget(image_label, row, col)
                
                # Atualiza a posição na grade
                col += 1
                if col > 2:  # Mudar para a próxima linha a cada 3 imagens
                    col = 0
                    row += 1

                # Atualiza a altura total
                total_height = (row + 1) * (max_size + 10)  # Adiciona uma margem para espaçamento

            except Exception as e:
                print(f"Erro ao carregar a imagem {path}: {e}")
                continue
        
        # Ajusta a altura mínima do QScrollArea
        self.scroll_area.setMinimumHeight(total_height)

    def convert_images(self):
        output_format = self.output_format.currentText().upper()
        if output_format not in ["JPEG", "PNG"]:
            QMessageBox.critical(self, "Erro", "Formato de saída inválido.")
            return

        # Inicializa e inicia o WorkerThread
        self.worker = WorkerThread(self.image_paths, output_format)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_conversion_finished(self):
        successful_conversions = self.worker.successful_conversions
        failed_conversions = self.worker.failed_conversions

        if successful_conversions:
            QMessageBox.information(self, "Sucesso", f"Imagens convertidas com sucesso:\n{', '.join(successful_conversions)}")
        if failed_conversions:
            QMessageBox.critical(self, "Erro", f"Falha na conversão das seguintes imagens:\n{', '.join(failed_conversions)}")

        self.go_back()

    def go_back(self):
        self.close()
        self.parent_app.show()
