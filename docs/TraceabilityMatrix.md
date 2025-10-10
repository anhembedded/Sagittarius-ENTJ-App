# Requirements Traceability Matrix

## 1. Introduction

### 1.1 Purpose
This document provides a traceability matrix to ensure that all requirements specified in the Software Requirements Specification (SRS) are addressed by the system's design and verified by a test case. This matrix links requirements to architectural components and the test cases that validate them.

---

## 2. Functional Requirements Traceability

| Requirement ID | Requirement Description                               | Architectural/Design Component(s)                                    | Verification Method (Test Case)                                                              |
|:---------------|:------------------------------------------------------|:---------------------------------------------------------------------|:---------------------------------------------------------------------------------------------|
| **FR-01**      | Scan a source directory and its subdirectories.       | `Model.scan_directory`                                               | `tests/test_model.py::TestModel.test_scan_directory`                                         |
| **FR-02**      | Filter files based on user-defined extensions.        | `Model.scan_directory`                                               | `tests/test_model.py::TestModel.test_scan_directory`                                         |
| **FR-03**      | Encode file content to Base64.                        | `Model.scan_directory`                                               | `tests/test_model.py::TestModel.test_scan_directory`                                         |
| **FR-04**      | Save the snapshot to a JSON file.                     | `Model.save_database`                                                | `tests/test_model.py::TestModel.test_save_and_load_database`                                 |
| **FR-05**      | Load a snapshot from a JSON file.                     | `Model.load_database`                                                | `tests/test_model.py::TestModel.test_save_and_load_database`                                 |
| **FR-06**      | Recreate the directory structure and files.           | `Model.recreate_from_database`                                       | `tests/test_model.py::TestModel.test_recreate_from_database`                                 |
| **FR-07**      | Provide a Graphical User Interface (GUI).             | `View` class, `PySide6`                                              | Manual Verification: Running the application (`python src/main.py`)                          |
| **FR-08**      | Provide file/directory selection dialogs.             | `View._browse_*` methods                                             | Manual Verification: Clicking the browse buttons in the UI.                                  |
| **FR-09**      | Allow adding/removing file extensions.                | `ViewModel.add_extension`, `ViewModel.remove_extension`, `View` widgets | `tests/test_viewmodel.py::TestViewModel.test_add_extension`, `...test_remove_extension`      |
| **FR-10**      | Perform long-running operations asynchronously.       | `Worker`, `QThreadPool`, `ViewModel._run_task`                       | Manual Verification: Observing UI responsiveness during a large scan.                        |
| **FR-11**      | Display a progress bar and operation log.             | `View` (ProgressBar, Log), `ViewModel` (signals), `Worker` (signals) | Manual Verification: Observing the log and progress bar during an operation.                 |
| **FR-12**      | Allow switching between 'light' and 'dark' themes.    | `ViewModel.theme`, `View._apply_theme`, `src/themes/`                | `tests/test_viewmodel.py::TestViewModel.test_set_theme`, Manual Verification in the UI.      |

---

## 3. Non-Functional Requirements Traceability

| Requirement ID | Requirement Description                               | Architectural/Design Component(s)                                    | Verification Method (Test Case)                                                              |
|:---------------|:------------------------------------------------------|:---------------------------------------------------------------------|:---------------------------------------------------------------------------------------------|
| **NFR-01**     | Buildable and runnable on Windows and Linux.          | `build.py`, Python standard libraries, `PyInstaller`                 | Manual Verification: Running `python build.py` on both platforms.                            |
| **NFR-02**     | Source code structured using MVVM.                    | SAD/SDD documents, `src` directory structure                         | Code Review and inspection of the source tree.                                               |
| **NFR-03**     | Dependencies defined in `requirements.txt`.           | `requirements.txt` file                                              | Successful execution of `pip install -r requirements.txt`.                                   |
| **NFR-04**     | Core logic verified by automated unit tests.          | `tests/` directory, `test_model.py`, `test_viewmodel.py`             | Successful execution of the full test suite (`python -m unittest discover tests`).           |
| **NFR-05**     | User configuration persisted between sessions.        | `ViewModel`, `QSettings`                                             | `tests/test_viewmodel.py` (path and theme tests), Manual Verification.                       |
| **NFR-06**     | Intuitive GUI with clear user feedback.               | `View` class layout, status bar messages                             | Manual Verification / User Acceptance Testing.                                               |
| **NFR-07**     | Provide a single, cross-platform build script.        | `build.py`                                                           | Successful execution of `python build.py`.                                                   |