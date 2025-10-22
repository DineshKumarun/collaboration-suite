import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import tempfile
from src.file_sharing import FileTransfer, FileMetadata

def test_checksum_calculation():
    """Test file checksum calculation"""
    print("Testing checksum calculation...")
    
    # Create temporary test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("Test content for checksum")
        temp_file = f.name
    
    try:
        # Calculate checksum
        checksum = FileTransfer.calculate_checksum(temp_file)
        print(f"✓ Checksum calculated: {checksum}")
        
        # Calculate again - should be same
        checksum2 = FileTransfer.calculate_checksum(temp_file)
        
        if checksum == checksum2:
            print("✓ Checksum calculation test PASSED")
            return True
        else:
            print("❌ Checksums don't match")
            return False
    finally:
        os.unlink(temp_file)


def test_file_metadata():
    """Test file metadata handling"""
    print("\nTesting file metadata...")
    
    metadata = FileMetadata(
        filename="test.txt",
        filesize=1024,
        checksum="abc123",
        sender="Alice"
    )
    
    # Test JSON serialization
    json_str = metadata.to_json()
    print(f"✓ Metadata serialized: {json_str}")
    
    # Test deserialization
    metadata2 = FileMetadata.from_json(json_str)
    
    if (metadata2.filename == metadata.filename and 
        metadata2.filesize == metadata.filesize and
        metadata2.checksum == metadata.checksum):
        print("✓ File metadata test PASSED")
        return True
    else:
        print("❌ Metadata doesn't match")
        return False


if __name__ == "__main__":
    print("=== File Transfer Tests ===\n")
    
    test1 = test_checksum_calculation()
    test2 = test_file_metadata()
    
    print("\n=== Test Summary ===")
    print(f"Checksum: {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"Metadata: {'✓ PASS' if test2 else '❌ FAIL'}")
