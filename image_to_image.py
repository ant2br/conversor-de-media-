from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox, QSpacerItem, QSizePolicy,
    QHBoxLayout, QListWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PIL import Image
import os

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, image_paths, output_format):
        super().__init__()
        self.image_paths = image_paths
        self.output_format = output_format

    def run(self):
        successful_conversions = []
        failed_conversions = []

        for idx, image_path in enumerate(self.image_paths):
            try:
                img = Image.open(image_path)
                
                # Converte para o formato de saída escolhido
                if img.mode != "RGB" and self.output_format == "JPEG":
                    img = img.convert("RGB")

                save_path = os.path.splitext(image_path)[0] + f".{self.output_format.lower()}"
                img.save(save_path, self.output_format)
                successful_conversions.append(os.path.basename(save_path))
                
            except Exception as e:
                failed_conversions.append(f"{os.path.basename(image_path)}: {e}")
            
            # Atualiza o progresso
            progress = int((idx + 1) / len(self.image_paths) * 100)
            self.progress.emit(progress)

        # Finaliza a execução
        self.finished.emit()
        self.successful_conversions = successful_conversions
        self.failed_conversions = failed_conversions

class ImageToImageConverter(QWidget):
    def __init__(self, parent_app):
        super().__init__()

        self.parent_app = parent_app
        self.setWindowTitle("Converter Imagem para Imagem")
        self.setGeometry(100, 100, 600, 500)  # Aumenta o tamanho da janela para acomodar os campos maiores

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Adiciona um espaçador acima do label
        self.layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Label
        self.label = QLabel("Selecione imagens para converter")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 15px;")
        self.layout.addWidget(self.label)

        # Adiciona um espaçador entre o label e o botão de seleção
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

        # Adiciona um espaçador entre o botão de seleção e o combo box
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

        self.preview_list = QListWidget()
        self.layout.addWidget(self.preview_list)

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

        # Adiciona um espaçador entre o botão de conversão e o botão de voltar
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

        # Inicializa a lista de imagens
        self.image_paths = []

        # Configura o WorkerThread
        self.worker = None

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
            self.preview_list.clear()
            for path in self.image_paths:
                try:
                    # Cria um item para a lista
                    list_item = QListWidgetItem()
                    
                    # Cria um QLabel para a imagem
                    image_label = QLabel()
                    img = QImage(path)
                    pixmap = QPixmap.fromImage(img).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                    
                    # Configura o QLabel com o QPixmap
                    image_label.setPixmap(pixmap)
                    
                    # Configura o item da lista para mostrar o QLabel
                    self.preview_list.addItem(list_item)
                    self.preview_list.setItemWidget(list_item, image_label)
                except Exception:
                    continue
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

