import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import threading
from src.text_chat import MessageHandler, Message, ChatManager

def test_message_encoding():
    """Test message encoding/decoding"""
    print("Testing message encoding...")
    
    # Create message
    msg = MessageHandler.create_message("Alice", "Hello, World!")
    print(f"✓ Created message: {msg.sender}: {msg.content}")
    
    # Encode
    encoded = MessageHandler.encode_message(msg)
    print(f"✓ Encoded to {len(encoded)} bytes")
    
    # Decode
    decoded = MessageHandler.decode_message(encoded)
    print(f"✓ Decoded message: {decoded.sender}: {decoded.content}")
    
    # Verify
    if decoded.sender == msg.sender and decoded.content == msg.content:
        print("✓ Message encoding test PASSED")
        return True
    else:
        print("❌ Message encoding test FAILED")
        return False


def test_message_types():
    """Test different message types"""
    print("\nTesting message types...")
    
    # Text message
    text_msg = MessageHandler.create_message("Bob", "Regular message", msg_type="text")
    assert text_msg.message_type == "text"
    print("✓ Text message created")
    
    # System message
    sys_msg = MessageHandler.create_message("System", "User joined", msg_type="system")
    assert sys_msg.message_type == "system"
    print("✓ System message created")
    
    # File message
    file_msg = MessageHandler.create_message(
        "Charlie", 
        "document.pdf", 
        msg_type="file",
        metadata={"size": 1024, "type": "pdf"}
    )
    assert file_msg.message_type == "file"
    assert file_msg.metadata["size"] == 1024
    print("✓ File message created")
    
    print("✓ Message types test PASSED")
    return True


def test_message_history():
    """Test message history management"""
    print("\nTesting message history...")
    
    manager = ChatManager("TestUser")
    
    # Add messages
    for i in range(10):
        msg = MessageHandler.create_message("TestUser", f"Message {i}")
        manager.message_history.append(msg)
    
    print(f"✓ Added 10 messages to history")
    
    # Get history
    history = manager.get_history(limit=5)
    assert len(history) == 5
    print(f"✓ Retrieved last 5 messages")
    
    # Verify order
    assert history[-1].content == "Message 9"
    print("✓ Messages in correct order")
    
    print("✓ Message history test PASSED")
    return True


def test_chat_formatting():
    """Test message formatting"""
    print("\nTesting message formatting...")
    
    msg = MessageHandler.create_message("Alice", "Test message")
    
    # Test JSON conversion
    json_str = msg.to_json()
    assert "Alice" in json_str
    assert "Test message" in json_str
    print("✓ JSON serialization works")
    
    # Test time formatting
    time_str = msg.format_time()
    assert ":" in time_str  # Should have HH:MM:SS format
    print(f"✓ Time formatted: {time_str}")
    
    # Test dict conversion
    msg_dict = msg.to_dict()
    assert msg_dict["sender"] == "Alice"
    assert msg_dict["content"] == "Test message"
    print("✓ Dictionary conversion works")
    
    print("✓ Message formatting test PASSED")
    return True


if __name__ == "__main__":
    print("=== Chat Module Tests ===\n")
    
    test1 = test_message_encoding()
    test2 = test_message_types()
    test3 = test_message_history()
    test4 = test_chat_formatting()
    
    print("\n=== Test Summary ===")
    print(f"Message Encoding: {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"Message Types: {'✓ PASS' if test2 else '❌ FAIL'}")
    print(f"Message History: {'✓ PASS' if test3 else '❌ FAIL'}")
    print(f"Message Formatting: {'✓ PASS' if test4 else '❌ FAIL'}")
