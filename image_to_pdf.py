from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QProgressBar, QScrollArea, QGridLayout, QSizePolicy, QAbstractItemView, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize, QMimeData, QTimer
from PyQt6.QtGui import QPixmap, QImage, QDrag
from PIL import Image
import os

class ImageToPDFConverter(QWidget):
    def __init__(self, parent_app):
        super().__init__()

        self.parent_app = parent_app
        self.setWindowTitle("Converter Imagem para PDF")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Label
        self.label = QLabel("Selecione imagens para converter em PDF")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px;")
        self.layout.addWidget(self.label)

        # Botão de Seleção
        self.select_button = QPushButton("Selecionar Imagens")
        self.select_button.clicked.connect(self.select_images)
        self.select_button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px; 
                padding: 12px; 
                border-radius: 8px;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            """
        )
        self.layout.addWidget(self.select_button)

        # Barra de Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Botão de Conversão
        self.convert_button = QPushButton("Converter para PDF")
        self.convert_button.clicked.connect(self.convert_images)
        self.convert_button.setEnabled(False)
        self.convert_button.setStyleSheet(
            """
            QPushButton {
                font-size: 18px; 
                padding: 12px; 
                border-radius: 8px;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            """
        )
        self.layout.addWidget(self.convert_button)

        # Botão de Voltar
        self.back_button = QPushButton("Voltar ao Menu")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px; 
                padding: 12px; 
                border-radius: 8px;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            """
        )
        self.layout.addWidget(self.back_button)

        # Área de Exibição de Miniaturas
        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.thumbnail_list.setStyleSheet(
            """
            QListWidget::item {
                margin: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            """
        )
        self.thumbnail_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.thumbnail_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.thumbnail_list.setDragEnabled(True)
        self.thumbnail_list.setDropIndicatorShown(True)
        self.thumbnail_list.setAcceptDrops(True)
        self.layout.addWidget(self.thumbnail_list)

        # Inicializa a lista de imagens
        self.image_paths = []

    def select_images(self):
        selected_files, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar Imagens", "", "Arquivos de Imagem (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.ico *.webp *.ppm *.pgm)"
        )

        if selected_files:
            valid_images = [path for path in selected_files if self.is_valid_image(path)]

            if len(valid_images) < len(selected_files):
                invalid_images = [path for path in selected_files if path not in valid_images]
                QMessageBox.warning(
                    self,
                    "Aviso",
                    f"As seguintes imagens não são válidas e serão ignoradas:\n{', '.join(os.path.basename(path) for path in invalid_images)}"
                )

            # Adiciona novas imagens à lista existente, evitando duplicatas
            new_images = [path for path in valid_images if path not in self.image_paths]
            if new_images:
                self.image_paths.extend(new_images)
                self.update_label()
                self.display_thumbnails()

    def is_valid_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verifica se o arquivo é uma imagem válida
            return True
        except (IOError, SyntaxError):
            return False

    def update_label(self):
        image_count = len(self.image_paths)
        self.label.setText(f"{image_count} imagem(s) selecionada(s).")
        self.convert_button.setEnabled(image_count > 0)

    def display_thumbnails(self):
        self.thumbnail_list.clear()
        
        for image_path in self.image_paths:
            try:
                image = QImage(image_path)
                pixmap = QPixmap.fromImage(image)
                thumbnail = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                
                thumbnail_item = QListWidgetItem()
                thumbnail_item.setSizeHint(QSize(120, 120))
                thumbnail_item_widget = QLabel()
                thumbnail_item_widget.setPixmap(thumbnail)
                thumbnail_item_widget.setFixedSize(120, 120)
                self.thumbnail_list.addItem(thumbnail_item)
                self.thumbnail_list.setItemWidget(thumbnail_item, thumbnail_item_widget)

            except Exception as e:
                QMessageBox.warning(self, "Aviso", f"Falha ao carregar miniatura para {os.path.basename(image_path)}: {e}")

    def convert_images(self):
        if not self.image_paths:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        pdf_files = []
        total_images = len(self.image_paths)
        
        for idx, image_path in enumerate(self.image_paths):
            try:
                with Image.open(image_path) as img:
                    img = img.convert('RGB')  # Converte a imagem para o modo RGB se necessário
                    pdf_files.append(img)
                    
                    # Atualiza a barra de progresso
                    progress = int((idx + 1) / total_images * 100)
                    self.progress_bar.setValue(progress)
            except Exception as e:
                QMessageBox.warning(self, "Aviso", f"Falha ao processar {os.path.basename(image_path)}: {e}")

        if pdf_files:
            save_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", "", "PDF files (*.pdf)")
            if save_path:
                try:
                    pdf_files[0].save(
                        save_path,
                        save_all=True,
                        append_images=pdf_files[1:],
                        resolution=100.0,
                        optimize=True
                    )
                    QMessageBox.information(self, "Sucesso", f"PDF criado com sucesso:\n{os.path.basename(save_path)}")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Falha ao criar PDF: {e}")

        self.progress_bar.setVisible(False)
        self.go_back()

    def go_back(self):
        self.close()
        self.parent_app.show()
