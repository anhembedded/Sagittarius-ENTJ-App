"""
Automated system test for password dialog integration.
Tests the complete flow: Load encrypted file -> Password dialog -> Decrypt -> Success
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.di_container import DIContainer
from src.presentation.view_models.paste_view_model import PasteViewModel
from src.shared.exceptions import DecryptionError, InvalidPasswordError


def test_load_encrypted_with_password():
    """Test loading encrypted file triggers password dialog."""
    
    print("=" * 70)
    print("AUTOMATED TEST: Password Dialog Integration")
    print("=" * 70)
    print()
    
    # Create application
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Setup
    container = DIContainer()
    viewmodel = PasteViewModel(container)
    
    file_path = "C:/Users/hoang/Documents/WorkDir/Sagittarius-ENTJ-App/TestObj"
    test_password = "test123"  # Adjust this to your actual password
    
    # Track what happened
    results = {
        'load_error_called': False,
        'error_msg': None,
        'exception_type': None,
        'load_completed': False,
        'test_passed': False
    }
    
    def on_load_error(error_msg: str, exception: object):
        """Handle load error - should get DecryptionError first."""
        results['load_error_called'] = True
        results['error_msg'] = error_msg
        results['exception_type'] = type(exception).__name__ if exception else None
        
        print(f"✅ Step 1: Load error received")
        print(f"   Error message: {error_msg[:100]}...")
        print(f"   Exception type: {results['exception_type']}")
        
        # Check if it's DecryptionError
        if isinstance(exception, DecryptionError):
            print(f"✅ Step 2: DecryptionError detected correctly")
            
            # Simulate password dialog - user enters password
            print(f"✅ Step 3: Simulating password entry: '{test_password}'")
            
            # Retry with password
            print(f"✅ Step 4: Retrying load with password...")
            viewmodel.load_snapshot(file_path, test_password)
        else:
            print(f"❌ FAIL: Expected DecryptionError, got {results['exception_type']}")
            results['test_passed'] = False
            app.quit()
    
    def on_load_completed(snapshot):
        """Handle successful load."""
        results['load_completed'] = True
        
        print(f"✅ Step 5: Load completed successfully!")
        print(f"   Files: {snapshot.get_file_count()}")
        print(f"   Directories: {snapshot.get_directory_count()}")
        print(f"   Root: {snapshot.root_path}")
        
        results['test_passed'] = True
        
        # Success - quit
        QTimer.singleShot(100, app.quit)
    
    def on_timeout():
        """Timeout if test takes too long."""
        print("\n❌ TIMEOUT: Test took too long (10 seconds)")
        results['test_passed'] = False
        app.quit()
    
    # Connect signals
    viewmodel.load_error.connect(on_load_error)
    viewmodel.load_completed.connect(on_load_completed)
    
    # Set timeout
    QTimer.singleShot(10000, on_timeout)
    
    # Start test
    print("🚀 Starting test...")
    print(f"📄 File: {file_path}")
    print(f"🔑 Test password: {test_password}")
    print()
    
    # Attempt to load encrypted file
    print("▶️  Step 0: Attempting to load encrypted file...")
    viewmodel.load_snapshot(file_path)
    
    # Run event loop
    app.exec()
    
    # Print results
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Load error called: {results['load_error_called']}")
    print(f"Exception type: {results['exception_type']}")
    print(f"Load completed: {results['load_completed']}")
    print(f"Test passed: {results['test_passed']}")
    print()
    
    if results['test_passed']:
        print("🎉 ✅ ALL TESTS PASSED!")
        print()
        print("Summary:")
        print("  1. ✅ Encrypted file triggered DecryptionError")
        print("  2. ✅ Password was provided")
        print("  3. ✅ File loaded successfully with correct password")
        return 0
    else:
        print("❌ TEST FAILED")
        if not results['load_error_called']:
            print("  - Load error was not triggered")
        if results['exception_type'] != 'DecryptionError':
            print(f"  - Wrong exception type: {results['exception_type']}")
        if not results['load_completed']:
            print("  - Load did not complete successfully")
        return 1


def test_wrong_password():
    """Test that wrong password triggers InvalidPasswordError."""
    
    print("=" * 70)
    print("AUTOMATED TEST: Wrong Password Handling")
    print("=" * 70)
    print()
    
    # Create application
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Setup
    container = DIContainer()
    viewmodel = PasteViewModel(container)
    
    file_path = "C:/Users/hoang/Documents/WorkDir/Sagittarius-ENTJ-App/TestObj"
    wrong_password = "wrongpassword123"
    
    # Track what happened
    results = {
        'first_error': None,
        'second_error': None,
        'test_passed': False
    }
    
    error_count = [0]  # Use list to make it mutable in nested function
    
    def on_load_error(error_msg: str, exception: object):
        """Handle load errors."""
        error_count[0] += 1
        
        if error_count[0] == 1:
            # First error - should be DecryptionError
            results['first_error'] = type(exception).__name__
            print(f"✅ Step 1: First error = {results['first_error']}")
            
            if isinstance(exception, DecryptionError):
                print(f"✅ Step 2: Trying with WRONG password...")
                viewmodel.load_snapshot(file_path, wrong_password)
        
        elif error_count[0] == 2:
            # Second error - should be InvalidPasswordError
            results['second_error'] = type(exception).__name__
            print(f"✅ Step 3: Second error = {results['second_error']}")
            
            if isinstance(exception, InvalidPasswordError):
                print(f"✅ Step 4: InvalidPasswordError correctly raised!")
                results['test_passed'] = True
            else:
                print(f"❌ Expected InvalidPasswordError, got {results['second_error']}")
            
            # Done
            QTimer.singleShot(100, app.quit)
    
    # Connect signal
    viewmodel.load_error.connect(on_load_error)
    
    # Set timeout
    QTimer.singleShot(10000, lambda: (print("\n❌ TIMEOUT"), app.quit()))
    
    # Start test
    print("🚀 Starting wrong password test...")
    print(f"📄 File: {file_path}")
    print(f"🔑 Wrong password: {wrong_password}")
    print()
    
    viewmodel.load_snapshot(file_path)
    
    # Run event loop
    app.exec()
    
    # Print results
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"First error: {results['first_error']}")
    print(f"Second error: {results['second_error']}")
    print(f"Test passed: {results['test_passed']}")
    print()
    
    if results['test_passed']:
        print("🎉 ✅ WRONG PASSWORD TEST PASSED!")
        return 0
    else:
        print("❌ TEST FAILED")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='System test for password dialog')
    parser.add_argument('--test', choices=['correct', 'wrong', 'both'], 
                       default='both', help='Which test to run')
    
    args = parser.parse_args()
    
    if args.test in ['correct', 'both']:
        result1 = test_load_encrypted_with_password()
        if result1 != 0:
            sys.exit(result1)
    
    if args.test in ['wrong', 'both']:
        result2 = test_wrong_password()
        sys.exit(result2)
