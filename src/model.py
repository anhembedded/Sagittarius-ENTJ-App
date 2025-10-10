import os
import base64
import json


# ------------------------ Model ------------------------#
class Model:
    """Handles data storage, file scanning, and recreation."""
    def __init__(self):
        """Initializes the model with an empty database."""
        self.database = {
            'directories': [],
            'files': []
        }

    # Modified to accept progress_callback and file_log_callback
    def scan_directory(self, root_dir, extensions, progress_callback=None, file_log_callback=None):
        """
        Scans the directory, encodes files, reports progress, and logs files.

        Args:
            root_dir (str): The directory to scan.
            extensions (list): List of file extensions (lowercase) to include.
            progress_callback (callable, optional): Reports progress (current, total).
            file_log_callback (callable, optional): Logs individual file actions.
        """
        # Reset database for a new scan
        self.database = {
            'directories': [],
            'files': []
        }
        # Ensure extensions are lowercase for case-insensitive matching
        extensions = [ext.lower() for ext in extensions]

        if file_log_callback:
            file_log_callback(f"🔍 Starting scan in: {root_dir}")

        # --- First Pass: Count matching files for progress bar ---
        total_files_to_process = 0
        if progress_callback:
            if file_log_callback:
                file_log_callback("⏳ Counting files for progress...")
            try:
                for _, _, filenames in os.walk(root_dir):
                    for filename in filenames:
                        _ , ext_part = os.path.splitext(filename)
                        if ext_part and ext_part.lower() in extensions:
                            total_files_to_process += 1
            except OSError as e:
                 if file_log_callback:
                    file_log_callback(f"❌ Error during file counting: {e}")
                 raise # Re-raise the error to be caught by the worker
            progress_callback(0, total_files_to_process) # Initialize progress
            if file_log_callback:
                file_log_callback(f"🔢 Found {total_files_to_process} files matching extensions.")
        # --- End First Pass ---


        # --- Second Pass: Collect directories and process files ---
        processed_files_count = 0
        try:
            # Collect directories first to ensure structure exists if needed later
            for dirpath, _, _ in os.walk(root_dir):
                # Calculate relative path from the root directory
                rel_dir = os.path.relpath(dirpath, root_dir)
                # Store only non-root relative paths
                if rel_dir and rel_dir != '.':
                    # Normalize path separators for consistency
                    self.database['directories'].append(rel_dir.replace(os.sep, '/'))

            # Collect and encode files
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    _ , ext_part = os.path.splitext(filename)
                    # Skip files without extensions
                    if not ext_part: continue
                    ext = ext_part.lower()

                    # Process only files with matching extensions
                    if ext in extensions:
                        file_path = os.path.join(dirpath, filename)
                        # Calculate relative path for storage
                        rel_path = os.path.relpath(file_path, root_dir).replace(os.sep, '/')
                        try:
                            # Read file content as binary
                            with open(file_path, 'rb') as f:
                                content = f.read()
                            # Encode content in Base64
                            content_b64 = base64.b64encode(content).decode('utf-8')
                            # Store file info in the database
                            self.database['files'].append({
                                'path': rel_path,
                                'content_base64': content_b64
                            })
                            processed_files_count += 1
                            if file_log_callback:
                                file_log_callback(f"  [Encode] -> {rel_path}")
                            if progress_callback:
                                # Update progress after successful processing
                                progress_callback(processed_files_count, total_files_to_process)

                        except Exception as e:
                            # Log errors encountered during file reading/encoding
                            if file_log_callback:
                                file_log_callback(f"  [Error reading {rel_path}] -> {e}")
                            # Decide if errors should count towards progress (currently they don't)

        except OSError as e:
            if file_log_callback:
                file_log_callback(f"❌ Error during directory walk: {e}")
            raise # Re-raise the error

        if file_log_callback:
            file_log_callback(f"📊 Scan complete. Found {len(self.database['directories'])} subdirs and encoded {processed_files_count} files.")
        # --- End Second Pass ---

    def save_database(self, json_path):
        """Saves the current database to a JSON file."""
        try:
            # Ensure the directory for the JSON file exists
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2)
        except OSError as e:
            # Log or raise error if saving fails
            print(f"Error saving database to {json_path}: {e}") # Simple print, consider logging
            raise

    def load_database(self, json_path):
        """Loads the database from a JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
        except FileNotFoundError:
            print(f"Error: Database file not found at {json_path}")
            self.database = {'directories': [], 'files': []} # Reset database
            raise
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_path}: {e}")
            self.database = {'directories': [], 'files': []} # Reset database
            raise
        except Exception as e:
            print(f"An unexpected error occurred loading database: {e}")
            self.database = {'directories': [], 'files': []} # Reset database
            raise


    # Modified to accept progress_callback and file_log_callback
    def recreate_from_database(self, output_dir, progress_callback=None, file_log_callback=None):
        """
        Recreates directory structure and files from the loaded database.

        Args:
            output_dir (str): The root directory to recreate into.
            progress_callback (callable, optional): Reports progress (current, total).
            file_log_callback (callable, optional): Logs individual file actions.
        """
        if file_log_callback:
            file_log_callback(f"🏗️ Starting recreation in: {output_dir}")

        # --- Setup Progress ---
        files_to_recreate = self.database.get('files', [])
        total_files_to_process = len(files_to_recreate)
        processed_files_count = 0
        if progress_callback:
            progress_callback(0, total_files_to_process) # Initialize progress
        # --- End Setup Progress ---


        # --- Create directories ---
        dir_count = 0
        try:
            # Ensure the main output directory exists
            os.makedirs(output_dir, exist_ok=True)
            # Create all subdirectories listed in the database
            for rel_dir in self.database.get('directories', []):
                # Skip empty or '.' relative paths
                if rel_dir and rel_dir != '.':
                    try:
                        # Construct full path and create directory
                        dir_path = os.path.join(output_dir, rel_dir.replace('/', os.sep)) # Use OS-specific separator
                        os.makedirs(dir_path, exist_ok=True)
                        dir_count += 1
                    except Exception as e:
                        # Log errors during directory creation
                        if file_log_callback:
                            file_log_callback(f"  [Error creating dir {rel_dir}] -> {e}")
        except OSError as e:
             if file_log_callback:
                file_log_callback(f"❌ Error creating base output directory {output_dir}: {e}")
             raise
        # --- End Create directories ---


        # --- Create files ---
        for file_info in files_to_recreate:
            rel_path = file_info.get('path')
            content_b64 = file_info.get('content_base64')

            # Validate file information
            if not rel_path or content_b64 is None:
                if file_log_callback:
                    file_log_callback("  [Skipping file] -> Missing path or content in database.")
                # Decide if skipped files affect progress total (currently they don't reduce total)
                continue

            # Construct full file path
            file_path = os.path.join(output_dir, rel_path.replace('/', os.sep)) # Use OS-specific separator
            file_dir = os.path.dirname(file_path)

            # Ensure the file's directory exists
            if file_dir:
                try:
                    os.makedirs(file_dir, exist_ok=True)
                except Exception as e:
                    if file_log_callback:
                        file_log_callback(f"  [Error creating dir for file {rel_path}] -> {e}")
                    # Skip this file if its directory cannot be created
                    continue

            # Decode and write the file content
            try:
                content = base64.b64decode(content_b64)
                with open(file_path, 'wb') as f:
                    f.write(content)
                processed_files_count += 1
                if file_log_callback:
                    file_log_callback(f"  [Decode] -> {rel_path}")
                if progress_callback:
                    # Update progress after successful file writing
                    progress_callback(processed_files_count, total_files_to_process)
            except Exception as e:
                if file_log_callback:
                    file_log_callback(f"  [Error writing {rel_path}] -> {e}")
                # Decide if errors should count towards progress (currently they don't)

        if file_log_callback:
            log_msg = f"✅ Recreation complete. Created {dir_count} dirs, processed {processed_files_count}/{total_files_to_process} files."
            file_log_callback(log_msg)
        # --- End Create files ---