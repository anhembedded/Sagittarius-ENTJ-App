# Software Requirements Specification (SRS) for Sagittarius-ENTJ

## 1. Introduction

### 1.1 Purpose
This document specifies the software requirements for the Sagittarius-ENTJ application. Its purpose is to provide a detailed description of the application's functional and non-functional requirements. The application is a desktop utility designed to create a "snapshot" of a directory structure and its file contents, save it to a JSON file, and recreate it elsewhere.

### 1.2 Scope
The application will:
- Scan a source directory based on user-defined file extensions.
- Save the directory structure and Base64-encoded file contents to a JSON file.
- Recreate the directory and files from a JSON snapshot to a specified output location.
- Provide a responsive Graphical User Interface (GUI) with features for theme switching and progress monitoring.
- Be buildable and runnable on both Windows and Linux.
- Be well-tested and maintainable through an MVVM architecture.

### 1.3 Definitions, Acronyms, and Abbreviations
- **SRS**: Software Requirements Specification
- **SAD**: Software Architecture Document
- **SDD**: Software Design Document
- **MVVM**: Model-View-ViewModel
- **GUI**: Graphical User Interface
- **QSS**: Qt Style Sheets
- **JSON**: JavaScript Object Notation
- **Base64**: A binary-to-text encoding scheme.

---

## 2. Overall Description

### 2.1 Product Perspective
The Sagittarius-ENTJ application is a self-contained desktop utility. It is designed for users who need to archive or transfer specific parts of a directory tree without copying the entire contents. It improves upon manual copy-paste operations by allowing precise filtering by file type and packaging the result into a single, portable file.

### 2.2 Product Functions
- **Snapshot Creation:** Scan a directory, filter by extensions, and save the result.
- **Snapshot Recreation:** Load a snapshot and restore the directory and files.
- **Configuration:** Manage file extensions and UI preferences (paths, theme).
- **User Feedback:** Display real-time progress, logs, and status messages.
- **Build Automation:** Package the application into a single executable.

### 2.3 User Characteristics
The target users are developers, system administrators, and other technical users who are comfortable with file system concepts and need a tool for selective data archival and replication.

---

## 3. Specific Requirements

### 3.1 Functional Requirements

| ID      | Requirement                                                                                             |
|---------|---------------------------------------------------------------------------------------------------------|
| **FR-01** | The system shall scan a user-specified source directory and all its subdirectories.                       |
| **FR-02** | The system shall filter files during the scan, including only those with user-defined extensions.         |
| **FR-03** | The system shall encode the content of all included files into Base64 format for storage.                 |
| **FR-04** | The system shall save the scanned directory structure and encoded file data into a single JSON file.      |
| **FR-05** | The system shall load a directory snapshot from a user-specified JSON file.                               |
| **FR-06** | The system shall recreate the full directory structure and decode/write all files from a loaded snapshot. |
| **FR-07** | The system shall provide a Graphical User Interface (GUI) for all user interactions.                      |
| **FR-08** | The GUI shall provide file/directory dialogs for selecting all required paths.                            |
| **FR-09** | The GUI shall allow users to add and remove file extensions from the inclusion list.                      |
| **FR-10** | The system shall perform long-running operations (scan, recreate) asynchronously to keep the UI responsive. |
| **FR-11** | The GUI shall display a progress bar and a log of operations to provide real-time user feedback.          |
| **FR-12** | The GUI shall allow the user to switch between a 'light' and a 'dark' visual theme.                       |

### 3.2 Non-Functional Requirements

| ID      | Requirement                                                                                             |
|---------|---------------------------------------------------------------------------------------------------------|
| **NFR-01**| The application must be buildable and runnable on both Windows and Linux operating systems.               |
| **NFR-02**| The source code shall be structured using the Model-View-ViewModel (MVVM) architecture for maintainability.|
| **NFR-03**| Project dependencies shall be explicitly defined in a `requirements.txt` file.                            |
| **NFR-04**| Core application logic (Model, ViewModel) shall be verified by a suite of automated unit tests.           |
| **NFR-05**| User configuration (paths, extensions, theme) shall be persisted between application sessions.            |
| **NFR-06**| The GUI shall be intuitive and provide clear status messages for user actions, successes, and errors.     |
| **NFR-07**| The project shall provide a single, cross-platform script to automate the build process into an executable.|