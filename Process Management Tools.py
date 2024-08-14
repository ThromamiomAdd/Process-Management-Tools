import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QLineEdit, QDialog, QComboBox, QListWidgetItem
from PyQt5.QtGui import QIcon, QFont, QColor
import psutil

class ProcessManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show_warning_message()
        self.language = "English"  # 默认语言

    def show_warning_message(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("提示")
        msg_box.setText("1. 本软件仅供学习使用，请勿作商业用途。\n \n2. 为了确保软件正常运行，请使用管理员身份运行。\n \n3. 软件作者不对使用本软件造成的任何损失负责。\n4.请谨慎使用，千万不要结束系统进程svchost.exe")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setMinimumSize(400, 200)
        msg_box.exec_()

    def initUI(self):
        self.setWindowTitle("Process Management Tools")
        
        main_layout = QVBoxLayout()
        self.process_list = QListWidget()
        main_layout.addWidget(self.process_list)

        info_layout = QHBoxLayout()
        self.pid_label = QLabel("Selected Process ID: None")
        self.name_label = QLabel("Process Name: None")
        self.mem_label = QLabel("Memory Usage: None")
        self.cpu_label = QLabel("CPU Usage: None")
        info_layout.addWidget(self.pid_label)
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.mem_label)
        info_layout.addWidget(self.cpu_label)
        main_layout.addLayout(info_layout)
        font = QFont()
        font.setFamily("KaiTi")  # 设置字体家族
        font.setPointSize(10)    # 设置字体大小

        button_layout = QHBoxLayout()
        self.list_processes_button = QPushButton("List Processes")
        self.list_processes_button.clicked.connect(self.list_processes)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.open_refresh_dialog)
        self.kill_button = QPushButton("Kill Process")
        self.kill_button.clicked.connect(self.open_kill_dialog)
        self.start_process_button = QPushButton("Start Process")
        self.start_process_button.clicked.connect(self.open_start_process_dialog)
        button_layout.addWidget(self.list_processes_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.kill_button)
        button_layout.addWidget(self.start_process_button)
        main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.process_list.itemSelectionChanged.connect(self.on_select)
        self.pid_label.setFont(font)
        self.name_label.setFont(font)
        self.mem_label.setFont(font)
        self.cpu_label.setFont(font)
        self.list_processes_button.setFont(font)
        self.refresh_button.setFont(font)
        self.kill_button.setFont(font)
        self.start_process_button.setFont(font)

        # 添加语言选择下拉框
        self.language_combo = QComboBox()
        self.language_combo.addItem("Chinese")
        self.language_combo.addItem("English")
        self.language_combo.currentTextChanged.connect(self.change_language)
        main_layout.addWidget(self.language_combo)
        # 添加版权信息
        copyright_label = QLabel("Copyright @ThromamiomAdd 2024")
        main_layout.addWidget(copyright_label)  
        
    def change_language(self, language):
        self.language = language
        self.update_ui_texts()

    def update_ui_texts(self):
        if self.language == "Chinese":
            self.setWindowTitle("进程管理器")
            self.list_processes_button.setText("列出进程")
            self.refresh_button.setText("刷新")
            self.kill_button.setText("结束进程")
            self.start_process_button.setText("启动进程")
            self.pid_label.setText("选择的进程ID: None")
            self.name_label.setText("进程名称: None")
            self.mem_label.setText("内存使用: None")
            self.cpu_label.setText("CPU使用: None")
        elif self.language == "English":
            self.setWindowTitle("Process Manager")
            self.list_processes_button.setText("List Processes")
            self.refresh_button.setText("Refresh")
            self.kill_button.setText("Kill Process")
            self.start_process_button.setText("Start Process")
            self.pid_label.setText("Selected Process ID: None")
            self.name_label.setText("Process Name: None")
            self.mem_label.setText("Memory Usage: None")
            self.cpu_label.setText("CPU Usage: None")

    def open_refresh_dialog(self):
        self.list_processes()

    def open_kill_dialog(self):
        dialog = KillProcessDialog(self)
        dialog.exec_()

    def open_start_process_dialog(self):
        dialog = StartProcessDialog(self)
        dialog.exec_()

    def kill_process(self, process):
        try:
            process.kill()
            QMessageBox.information(self, "Success", f"Process {process.pid} has been killed.")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            QMessageBox.critical(self, "Error", f"Failed to kill process: {e}")

    def list_processes(self):
        self.process_list.clear()
        for proc in psutil.process_iter(['pid', 'name']):
            item = QListWidgetItem(f"{proc.info['pid']} - {proc.info['name']}")
            if proc.info['name'] in ['System', 'svchost.exe', 'csrss.exe', 'lsass.exe']:  # 特定的系统进程
                item.setForeground(QColor(255, 0, 0))  # 设置为红色
            self.process_list.addItem(item)

    def on_select(self):
        selection = self.process_list.selectedItems()
        if selection:
            pid = int(selection[0].text().split(" - ")[0])
            try:
                process = psutil.Process(pid)
                self.pid_label.setText(f"Selected Process ID: {pid}")
                self.name_label.setText(f"Process Name: {process.name()}")
                self.mem_label.setText(f"Memory Usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                self.cpu_label.setText(f"CPU Usage: {process.cpu_percent(interval=0.1)}%")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                QMessageBox.critical(self, "Error", f"Failed to retrieve process info: {e}")
                self.reset_labels()

    def reset_labels(self):
        self.pid_label.setText(f"Selected Process ID: None")
        self.name_label.setText("Process Name: None")
        self.mem_label.setText("Memory Usage: None")
        self.cpu_label.setText("CPU Usage: None")

class KillProcessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Kill Process")

        self.pid_input = QLineEdit()
        self.pid_input.setPlaceholderText("Enter Process ID")
        layout.addWidget(QLabel("Process ID:"))
        layout.addWidget(self.pid_input)

        kill_button = QPushButton("Kill")
        kill_button.clicked.connect(self.confirm_kill)
        layout.addWidget(kill_button)

        self.setLayout(layout)

    def confirm_kill(self):
        confirm_msg = QMessageBox.question(self, "Confirmation", "This action is irreversible, are you sure you want to do this?", QMessageBox.Yes | QMessageBox.No)
        if confirm_msg == QMessageBox.Yes:
            self.kill_process()

    def kill_process(self):
        pid = int(self.pid_input.text())
        try:
            process = psutil.Process(pid)
            process.kill()
            QMessageBox.information(self, "Success", f"Process {pid} has been killed.")
            self.close()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            QMessageBox.critical(self, "Error", f"Failed to kill process: {e}")

class StartProcessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Start Process")
        font = QFont()
        font.setFamily("KaiTi")  # 设置字体家族
        font.setPointSize(10)    # 设置字体大小

        self.process_path_input = QLineEdit()
        self.process_path_input.setPlaceholderText("exe文件路径")
        layout.addWidget(QLabel("Process Path:"))
        layout.addWidget(self.process_path_input)

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_process)
        layout.addWidget(start_button)

        self.setLayout(layout)

    def start_process(self):
        process_path = self.process_path_input.text()
        if not process_path:
            QMessageBox.warning(self, "Warning", "请输入路径")
            return

        try:
            psutil.Popen(process_path)
            QMessageBox.information(self, "Success", f"进程已启动: {process_path}")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"启动进程失败: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProcessManager()
    ex.show()
    sys.exit(app.exec_())
