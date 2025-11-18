"""Main entry point for Sagittarius ENTJ application."""

import sys
from PySide6.QtWidgets import QApplication

from src.di_container import DIContainer
from src.presentation.views.main_window import MainWindow
from src.infrastructure.logging import setup_logger
from src.shared.constants import APP_NAME, APP_ORGANIZATION


def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logger('sagittarius_entj')
    logger.info("=" * 60)
    logger.info("Starting Sagittarius ENTJ - Directory Snapshot Manager")
    logger.info("=" * 60)
    
    try:
        # Create DI container
        container = DIContainer()
        logger.info("Dependency injection container initialized")
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setOrganizationName(APP_ORGANIZATION)
        
        # Set application style
        app.setStyle('Fusion')  # Modern cross-platform style
        
        # Create and show main window
        logger.info("Creating main window...")
        window = MainWindow(container)
        window.show()
        
        logger.info("Application started successfully")
        
        # Run application event loop
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.exception(f"Fatal error during application startup: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
