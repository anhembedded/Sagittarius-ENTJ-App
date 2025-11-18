"""Integration test for encryption workflow."""

import os
import tempfile
import shutil
from pathlib import Path

from src.infrastructure.encryption.aes_gcm_encryptor import AESGCMEncryptor
from src.infrastructure.persistence.json_repository import JsonSnapshotRepository
from src.infrastructure.encoding.base64_encoder import Base64Encoder
from src.domain.models.snapshot import DirectorySnapshot
from src.domain.models.file_entry import FileEntry


def test_encrypted_snapshot_workflow():
    """Test complete workflow: save encrypted → load encrypted → recreate."""
    
    # Setup
    password = "TestPassword123!"
    encoder = Base64Encoder()
    encryptor = AESGCMEncryptor()
    repository = JsonSnapshotRepository(encoder, encryptor)
    
    # Create temporary directories
    source_dir = tempfile.mkdtemp(prefix="test_source_")
    output_dir = tempfile.mkdtemp(prefix="test_output_")
    json_file = os.path.join(tempfile.gettempdir(), "test_encrypted_snapshot.json")
    
    try:
        # Create test files in source directory
        test_file_1 = os.path.join(source_dir, "test1.txt")
        test_file_2 = os.path.join(source_dir, "subdir", "test2.txt")
        
        os.makedirs(os.path.dirname(test_file_2), exist_ok=True)
        
        with open(test_file_1, 'w', encoding='utf-8') as f:
            f.write("Hello World!")
        
        with open(test_file_2, 'w', encoding='utf-8') as f:
            f.write("Hello from subdirectory!")
        
        # Step 1: Create snapshot
        print("📸 Creating snapshot...")
        files = []
        
        for root, dirs, filenames in os.walk(source_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, source_dir)
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                file_entry = FileEntry(
                    relative_path=rel_path,
                    content=content
                )
                files.append(file_entry)
        
        snapshot = DirectorySnapshot(
            root_path=source_dir,
            files=files
        )
        
        print(f"   Created snapshot with {len(files)} files")
        
        # Step 2: Save encrypted snapshot
        print(f"🔐 Saving encrypted snapshot to: {json_file}")
        repository.save(snapshot, json_file, password=password)
        
        # Verify file is encrypted (should not be readable JSON)
        with open(json_file, 'rb') as f:
            raw_data = f.read()
        
        assert raw_data.startswith(b"SAGENC"), "File should be encrypted with magic header"
        print("   ✅ Snapshot encrypted successfully")
        
        # Step 3: Load encrypted snapshot (without password - should fail)
        print("🔓 Testing load without password (should fail)...")
        try:
            repository.load(json_file, password=None)
            assert False, "Should have raised DecryptionError"
        except Exception as e:
            print(f"   ✅ Correctly raised error: {type(e).__name__}")
        
        # Step 4: Load encrypted snapshot (with correct password)
        print(f"🔓 Loading encrypted snapshot with password...")
        loaded_snapshot = repository.load(json_file, password=password)
        
        assert loaded_snapshot.get_file_count() == 2, "Should load 2 files"
        assert loaded_snapshot.root_path == source_dir, "Root path should match"
        print(f"   ✅ Loaded {loaded_snapshot.get_file_count()} files")
        
        # Step 5: Verify content
        print("📋 Verifying file contents...")
        for original, loaded in zip(snapshot.files, loaded_snapshot.files):
            assert original.relative_path == loaded.relative_path, f"Paths should match: {original.relative_path}"
            assert original.content == loaded.content, f"Contents should match for {original.relative_path}"
        print("   ✅ All file contents match")
        
        # Step 6: Recreate directory
        print(f"📂 Recreating directory to: {output_dir}")
        
        # Manually recreate files
        for file_entry in loaded_snapshot.files:
            output_path = os.path.join(output_dir, file_entry.relative_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(file_entry.content)
        
        # Step 7: Verify recreated files
        print("✔️  Verifying recreated files...")
        recreated_file_1 = os.path.join(output_dir, "test1.txt")
        recreated_file_2 = os.path.join(output_dir, "subdir", "test2.txt")
        
        assert os.path.exists(recreated_file_1), "test1.txt should exist"
        assert os.path.exists(recreated_file_2), "subdir/test2.txt should exist"
        
        with open(recreated_file_1, 'r', encoding='utf-8') as f:
            content1 = f.read()
        with open(recreated_file_2, 'r', encoding='utf-8') as f:
            content2 = f.read()
        
        assert content1 == "Hello World!", "test1.txt content should match"
        assert content2 == "Hello from subdirectory!", "test2.txt content should match"
        
        print("   ✅ All recreated files verified")
        
        print("\n🎉 ===== ENCRYPTION WORKFLOW TEST PASSED =====")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if os.path.exists(source_dir):
            shutil.rmtree(source_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        if os.path.exists(json_file):
            os.remove(json_file)
        print("\n🧹 Cleanup completed")


if __name__ == "__main__":
    print("=" * 60)
    print("ENCRYPTION INTEGRATION TEST")
    print("=" * 60)
    print()
    
    success = test_encrypted_snapshot_workflow()
    
    exit(0 if success else 1)
