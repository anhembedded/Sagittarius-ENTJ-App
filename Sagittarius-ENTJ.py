import os
import base64
import json
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
							   QLineEdit, QPushButton, QListWidget, QListWidgetItem,
							   QTextEdit, QFileDialog, QMessageBox, QGroupBox,
							   QLabel, QFormLayout)
from PySide6.QtCore import Qt, QObject, Signal, QRunnable, QThreadPool


# ------------------------ Model ------------------------#
class Model:
	def __init__(self):
		self.database = {
			'directories': [],
			'files': []
		}

	def scan_directory(self, root_dir, extensions):
		self.database = {
			'directories': [],
			'files': []
		}
		extensions = [ext.lower() for ext in extensions]

		# Collect directories
		for dirpath, _, _ in os.walk(root_dir):
			rel_dir = os.path.relpath(dirpath, root_dir)
			if rel_dir == '.':
				rel_dir = ''
			self.database['directories'].append(rel_dir)

		# Collect files
		for dirpath, _, filenames in os.walk(root_dir):
			for filename in filenames:
				ext = os.path.splitext(filename)[1].lower()
				if ext in extensions:
					file_path = os.path.join(dirpath, filename)
					rel_path = os.path.relpath(file_path, root_dir)
					with open(file_path, 'rb') as f:
						content = f.read()
					content_b64 = base64.b64encode(content).decode('utf-8')
					self.database['files'].append({
						'path': rel_path,
						'content_base64': content_b64
					})

	def save_database(self, json_path):
		with open(json_path, 'w') as f:
			json.dump(self.database, f, indent=2)

	def load_database(self, json_path):
		with open(json_path, 'r') as f:
			self.database = json.load(f)

	def recreate_from_database(self, output_dir):
		# Create directories
		for rel_dir in self.database['directories']:
			dir_path = os.path.join(output_dir, rel_dir)
			os.makedirs(dir_path, exist_ok=True)

		# Create files
		for file_info in self.database['files']:
			file_path = os.path.join(output_dir, file_info['path'])
			content = base64.b64decode(file_info['content_base64'])
			with open(file_path, 'wb') as f:
				f.write(content)


# ------------------------ ViewModel ------------------------#
class ViewModel(QObject):
	message_logged = Signal(str)

	def __init__(self, model):
		super().__init__()
		self.model = model
		self._copy_source_dir = ''
		self._copy_json_path = ''
		self._paste_json_path = ''
		self._paste_output_dir = ''
		self._extensions = ['.txt', '.py']

	# Copy properties
	@property
	def copy_source_dir(self):
		return self._copy_source_dir

	@copy_source_dir.setter
	def copy_source_dir(self, value):
		if os.path.isdir(value):
			self._copy_source_dir = value

	@property
	def copy_json_path(self):
		return self._copy_json_path

	@copy_json_path.setter
	def copy_json_path(self, value):
		self._copy_json_path = value

	# Paste properties
	@property
	def paste_json_path(self):
		return self._paste_json_path

	@paste_json_path.setter
	def paste_json_path(self, value):
		self._paste_json_path = value

	@property
	def paste_output_dir(self):
		return self._paste_output_dir

	@paste_output_dir.setter
	def paste_output_dir(self, value):
		if os.path.isdir(value):
			self._paste_output_dir = value

	# Extensions management
	@property
	def extensions(self):
		return self._extensions.copy()

	def add_extension(self, ext):
		if ext and ext not in self._extensions:
			self._extensions.append(ext)

	def remove_extension(self, ext):
		if ext in self._extensions:
			self._extensions.remove(ext)

	def perform_copy(self):
		if not self._copy_source_dir:
			self.message_logged.emit("⚠️ Please select a source directory to copy")
			return
		if not self._copy_json_path:
			self.message_logged.emit("⚠️ Please select output JSON file path")
			return

		def copy_task():
			try:
				self.model.scan_directory(self._copy_source_dir, self._extensions)
				self.model.save_database(self._copy_json_path)
				self.message_logged.emit("✅ Copy completed successfully")
				self.message_logged.emit(f"💾 Database saved to: {self._copy_json_path}")
			except Exception as e:
				self.message_logged.emit(f"❌ Copy error: {str(e)}")

		self._run_task(copy_task)

	def perform_paste(self):
		if not self._paste_json_path:
			self.message_logged.emit("⚠️ Please select a database JSON file")
			return
		if not self._paste_output_dir:
			self.message_logged.emit("⚠️ Please select an output directory")
			return

		def paste_task():
			try:
				self.model.load_database(self._paste_json_path)
				self.model.recreate_from_database(self._paste_output_dir)
				self.message_logged.emit("✅ Paste completed successfully")
			except Exception as e:
				self.message_logged.emit(f"❌ Paste error: {str(e)}")

		self._run_task(paste_task)

	def _run_task(self, task):
		worker = Worker(task)
		worker.signals.error.connect(lambda e: self.message_logged.emit(f"❌ {e}"))
		QThreadPool.globalInstance().start(worker)


# ------------------------ Worker ------------------------#
class WorkerSignals(QObject):
	error = Signal(str)


class Worker(QRunnable):
	def __init__(self, task):
		super().__init__()
		self.task = task
		self.signals = WorkerSignals()

	def run(self):
		try:
			self.task()
		except Exception as e:
			self.signals.error.emit(str(e))


# ------------------------ View ------------------------#
class View(QWidget):
	def __init__(self, viewmodel):
		super().__init__()
		self.viewmodel = viewmodel
		self.init_ui()
		self.connect_signals()
		self.setMinimumSize(800, 600)

	def init_ui(self):
		self.setWindowTitle("Directory Snapshot Manager")
		layout = QVBoxLayout()

		# Copy Section
		copy_group = QGroupBox("Copy Operations")
		copy_layout = QFormLayout()

		self.copy_source_edit = QLineEdit()
		copy_layout.addRow("Source Directory:", self._create_browse_row(
			self.copy_source_edit, self._browse_copy_source, is_file=False))

		self.copy_json_edit = QLineEdit()
		copy_layout.addRow("Output JSON File:", self._create_browse_row(
			self.copy_json_edit, self._browse_copy_json, is_file=True))

		# Extensions
		self.ext_list = QListWidget()
		self.ext_list.setSelectionMode(QListWidget.ExtendedSelection)
		copy_layout.addRow("File Extensions:", self.ext_list)

		ext_control_layout = QHBoxLayout()
		self.ext_edit = QLineEdit()
		self.ext_edit.setPlaceholderText(".ext")
		ext_control_layout.addWidget(self.ext_edit)

		add_btn = QPushButton("Add")
		add_btn.clicked.connect(self._add_extension)
		ext_control_layout.addWidget(add_btn)

		remove_btn = QPushButton("Remove Selected")
		remove_btn.clicked.connect(self._remove_extensions)
		ext_control_layout.addWidget(remove_btn)
		copy_layout.addRow(ext_control_layout)

		self.copy_btn = QPushButton("Perform Copy")
		self.copy_btn.setStyleSheet("background-color: #4CAF50; color: white;")
		copy_layout.addRow(self.copy_btn)

		copy_group.setLayout(copy_layout)
		layout.addWidget(copy_group)

		# Paste Section
		paste_group = QGroupBox("Paste Operations")
		paste_layout = QFormLayout()

		self.paste_json_edit = QLineEdit()
		paste_layout.addRow("Database JSON File:", self._create_browse_row(
			self.paste_json_edit, self._browse_paste_json, is_file=True))

		self.paste_output_edit = QLineEdit()
		paste_layout.addRow("Output Directory:", self._create_browse_row(
			self.paste_output_edit, self._browse_paste_output, is_file=False))

		self.paste_btn = QPushButton("Perform Paste")
		self.paste_btn.setStyleSheet("background-color: #008CBA; color: white;")
		paste_layout.addRow(self.paste_btn)

		paste_group.setLayout(paste_layout)
		layout.addWidget(paste_group)

		# Log
		self.log = QTextEdit()
		self.log.setReadOnly(True)
		layout.addWidget(QLabel("Operation Log:"))
		layout.addWidget(self.log)

		self.setLayout(layout)

	def _create_browse_row(self, edit, handler, is_file):
		row = QHBoxLayout()
		row.addWidget(edit)
		btn = QPushButton("Browse...")
		btn.clicked.connect(handler)
		row.addWidget(btn)
		return row

	def connect_signals(self):
		# Copy signals
		self.copy_source_edit.textChanged.connect(
			lambda t: setattr(self.viewmodel, 'copy_source_dir', t))
		self.copy_json_edit.textChanged.connect(
			lambda t: setattr(self.viewmodel, 'copy_json_path', t))

		# Paste signals
		self.paste_json_edit.textChanged.connect(
			lambda t: setattr(self.viewmodel, 'paste_json_path', t))
		self.paste_output_edit.textChanged.connect(
			lambda t: setattr(self.viewmodel, 'paste_output_dir', t))

		# Buttons
		self.copy_btn.clicked.connect(self.viewmodel.perform_copy)
		self.paste_btn.clicked.connect(self.viewmodel.perform_paste)

		# Logging
		self.viewmodel.message_logged.connect(self.log.append)

	def _browse_copy_source(self):
		if dir := QFileDialog.getExistingDirectory(self, "Select Source Directory"):
			self.copy_source_edit.setText(dir)

	def _browse_copy_json(self):
		path, _ = QFileDialog.getSaveFileName(
			self, "Save Database File", "", "JSON Files (*.json)")
		if path:
			self.copy_json_edit.setText(path)

	def _browse_paste_json(self):
		path, _ = QFileDialog.getOpenFileName(
			self, "Select Database File", "", "JSON Files (*.json)")
		if path:
			self.paste_json_edit.setText(path)

	def _browse_paste_output(self):
		if dir := QFileDialog.getExistingDirectory(self, "Select Output Directory"):
			self.paste_output_edit.setText(dir)

	def _add_extension(self):
		ext = self.ext_edit.text().strip()
		if ext.startswith('.'):
			self.viewmodel.add_extension(ext.lower())
			self.ext_edit.clear()
			self._update_extensions_list()
		else:
			QMessageBox.warning(self, "Invalid Extension",
								"Extension must start with a dot (e.g., .txt)")

	def _remove_extensions(self):
		for item in self.ext_list.selectedItems():
			self.viewmodel.remove_extension(item.text())
		self._update_extensions_list()

	def _update_extensions_list(self):
		self.ext_list.clear()
		self.ext_list.addItems(sorted(self.viewmodel.extensions))


# ------------------------ Main ------------------------#
def main():
	app = QApplication([])
	model = Model()
	viewmodel = ViewModel(model)
	view = View(viewmodel)
	view.show()
	app.exec()


if __name__ == '__main__':
	main()