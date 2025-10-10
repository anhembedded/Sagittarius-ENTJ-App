import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.model import Model
from src.view import View
from src.viewmodel import ViewModel


# ------------------------ Main Application Entry Point ------------------------#
def main():
    """Sets up and runs the Qt application."""
    # Set application details used by QSettings
    QApplication.setOrganizationName("HoangAnhTran") # Use your name or company
    QApplication.setApplicationName("DirSnapshotApp_v3_Fixed") # Match ViewModel QSettings

    # Enable High DPI scaling for better visuals on modern displays
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # --- Instantiate MVC components ---
    model = Model()
    viewmodel = ViewModel(model)
    view = View(viewmodel)
    view.show() # Display the main window

    # --- Start the Qt event loop ---
    sys.exit(app.exec())


if __name__ == '__main__':
    main() # Run the main function when the script is executed