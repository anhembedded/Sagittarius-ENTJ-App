"""System test for encrypted snapshot load/save."""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.encryption.aes_gcm_encryptor import AESGCMEncryptor
from src.infrastructure.persistence.json_repository import JsonSnapshotRepository
from src.infrastructure.encoding.base64_encoder import Base64Encoder


def test_load_encrypted_file():
    """Test loading the encrypted TestObj file."""
    
    print("=" * 60)
    print("SYSTEM TEST: Load Encrypted Snapshot")
    print("=" * 60)
    print()
    
    # Setup
    file_path = "C:/Users/hoang/Documents/WorkDir/Sagittarius-ENTJ-App/TestObj"
    password = input("Enter password for TestObj: ")
    
    encoder = Base64Encoder()
    encryptor = AESGCMEncryptor()
    repository = JsonSnapshotRepository(encoder, encryptor)
    
    try:
        # Step 1: Check file exists
        print(f"1. Checking file exists: {file_path}")
        if not os.path.exists(file_path):
            print("   ❌ File not found!")
            return False
        print("   ✅ File exists")
        
        # Step 2: Read raw bytes
        print(f"\n2. Reading file (size: {os.path.getsize(file_path)} bytes)")
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        print(f"   ✅ Read {len(raw_data)} bytes")
        
        # Step 3: Check if encrypted
        print("\n3. Checking encryption status")
        is_encrypted = encryptor.is_encrypted(raw_data)
        print(f"   Is encrypted: {is_encrypted}")
        
        if is_encrypted:
            print(f"   Magic header: {raw_data[:6]}")
            print(f"   Version: {raw_data[6]}")
        
        # Step 4: Try to decrypt
        if is_encrypted and password:
            print(f"\n4. Attempting decryption...")
            try:
                decrypted_data = encryptor.decrypt(raw_data, password)
                print(f"   ✅ Decryption successful ({len(decrypted_data)} bytes)")
                
                # Try to parse JSON
                import json
                json_str = decrypted_data.decode('utf-8')
                data = json.loads(json_str)
                print(f"   ✅ JSON parsed successfully")
                print(f"   Files in snapshot: {len(data.get('files', []))}")
                
            except Exception as e:
                print(f"   ❌ Decryption failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Step 5: Load via repository
        print(f"\n5. Loading via repository...")
        try:
            snapshot = repository.load(file_path, password if is_encrypted else None)
            print(f"   ✅ Loaded successfully!")
            print(f"   Root path: {snapshot.root_path}")
            print(f"   Files: {snapshot.get_file_count()}")
            print(f"   Directories: {snapshot.get_directory_count()}")
            
            stats = snapshot.get_statistics()
            print(f"\n📊 Snapshot Statistics:")
            print(f"   Created: {stats['created_at']}")
            print(f"   Total size: {stats['total_size_bytes']:,} bytes")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Repository load failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_check_file_only():
    """Just check the file without loading."""
    
    print("=" * 60)
    print("QUICK FILE CHECK")
    print("=" * 60)
    print()
    
    file_path = "C:/Users/hoang/Documents/WorkDir/Sagittarius-ENTJ-App/TestObj"
    
    # Read first 100 bytes
    with open(file_path, 'rb') as f:
        header = f.read(100)
    
    print(f"File: {file_path}")
    print(f"Size: {os.path.getsize(file_path):,} bytes")
    print(f"\nFirst 100 bytes (hex):")
    
    # Print in hex format
    for i in range(0, len(header), 16):
        hex_part = ' '.join(f'{b:02x}' for b in header[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in header[i:i+16])
        print(f"{i:04x}:  {hex_part:<48}  {ascii_part}")
    
    # Check encryption
    encryptor = AESGCMEncryptor()
    is_encrypted = encryptor.is_encrypted(header)
    print(f"\nIs encrypted: {is_encrypted}")
    
    if header.startswith(b"SAGENC"):
        print("✅ Has correct magic header: SAGENC")
        print(f"Version: {header[6]}")
    else:
        print("❌ Wrong magic header:", header[:10])


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test encrypted snapshot loading')
    parser.add_argument('--quick', action='store_true', help='Just check file info')
    
    args = parser.parse_args()
    
    if args.quick:
        test_check_file_only()
    else:
        success = test_load_encrypted_file()
        exit(0 if success else 1)
