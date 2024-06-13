import sys
import uuid
import random_username.generate
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QMessageBox, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt, QFile, QTextStream
import minecraft_launcher_lib as mll
import os
import platform
import subprocess

class MinecraftLauncher(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()
        self.load_config()

    def initUI(self):
        self.setWindowTitle('DLauncher')
        self.setFixedSize(400, 300)  # Размер окна
        self.setStyleSheet("background-color: gray;")  # Цвет фона

        # Титул
        self.title_label = QLabel(self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setText('<span style="color: yellow;">D</span>Launcher')
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Ввода ника
        self.username_label = QLabel('Ваш псевданим:', self)
        self.username_label.setStyleSheet("color: white;")
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Введите свой псевданим')
        self.username_input.setStyleSheet("background-color: white; color: black;")
        
        # Выбор версий
        self.version_label = QLabel('Выберите версию:', self)
        self.version_label.setStyleSheet("color: white;")
        self.version_combo = QComboBox(self)
        self.version_combo.setStyleSheet("background-color: white; color: black;")
        self.update_versions_button = QPushButton('Обновить версии', self)
        self.update_versions_button.setStyleSheet("background-color: white; color: black;")
        self.update_versions_button.clicked.connect(self.update_versions)
        self.update_versions()

        # Запустить игру
        self.launch_button = QPushButton('Запустить', self)
        self.launch_button.setStyleSheet("background-color: white; color: black;")
        self.launch_button.clicked.connect(self.launch_game)

        # Открытие папки .minecraft
        self.open_folder_button = QPushButton('Открыть ".minecraft"', self)
        self.open_folder_button.setStyleSheet("background-color: white; color: black;")
        self.open_folder_button.clicked.connect(self.open_minecraft_folder)
        
        # Открытие папки .minecraft/mods
        self.open_mods_folder_button = QPushButton('Mods', self)
        self.open_mods_folder_button.setStyleSheet("background-color: white; color: black;")
        self.open_mods_folder_button.clicked.connect(self.open_mods_folder)

        # Настройка макета
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.version_label)
        layout.addWidget(self.version_combo)
        layout.addWidget(self.update_versions_button)
        layout.addWidget(self.launch_button)

        # Добавление кнопок открытия папок в макет
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_mods_folder_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.open_folder_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_config(self):
        try:
            with open('config.txt', 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    saved_username = lines[0].strip()
                    saved_version = lines[1].strip()
                    self.username_input.setText(saved_username)
                    if saved_version in [self.version_combo.itemText(i) for i in range(self.version_combo.count())]:
                        self.version_combo.setCurrentText(saved_version)
        except FileNotFoundError:
            pass

    def save_config(self):
        username = self.username_input.text()
        selected_version = self.version_combo.currentText()
        with open('config.txt', 'w') as f:
            f.write(f"{username}\n")
            f.write(f"{selected_version}\n")

    def update_versions(self):
        self.version_combo.clear()
        game_directory = os.path.expanduser("~/.minecraft")
        self.versions = mll.utils.get_available_versions(game_directory)
        for version in self.versions:
            self.version_combo.addItem(version["id"])

    def launch_game(self):
        username = self.username_input.text()
        if not username:
            username = random_username.generate.generate_username(1)[0]

        selected_version = self.version_combo.currentText()
        game_directory = os.path.expanduser("~/.minecraft")
        options = {
            "username": username,
            "uuid": str(uuid.uuid4()),
            "token": str(uuid.uuid4())
        }

        try:
            if QMessageBox.information(self, "Installing", f"Установка версии {selected_version}..."):
                mll.install.install_minecraft_version(selected_version, game_directory)

            command = mll.command.get_minecraft_command(selected_version, game_directory, options)
            print(f"Launching Minecraft with command: {command}")
            os.system(" ".join(command))
            QMessageBox.information(self, "Success", f"Версия: {selected_version}, имя: {username}")
            self.save_config()  # Сохранение конфигурации после успешного запуска
        except mll.exceptions.MinecraftVersionNotFound:
            QMessageBox.critical(self, "Error", f"Версия {selected_version} не установлена.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ошибка лаунчера: {str(e)}")

    def open_minecraft_folder(self):
        game_directory = os.path.expanduser("~/.minecraft")
        self.open_folder(game_directory)
        
    def open_mods_folder(self):
        mods_directory = os.path.expanduser("~/.minecraft/mods")
        if not os.path.exists(mods_directory):
            os.makedirs(mods_directory)
        self.open_folder(mods_directory)

    def open_folder(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux и другие Unix-подобные системы
            subprocess.Popen(["xdg-open", path])

def main():
    app = QApplication(sys.argv)
    launcher = MinecraftLauncher()
    launcher.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
