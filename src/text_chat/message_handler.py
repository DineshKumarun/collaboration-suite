import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Message:
    """Message data structure"""
    sender: str
    content: str
    timestamp: float
    message_type: str = "text"  # text, system, file
    metadata: Optional[Dict] = None
    
    def to_json(self) -> str:
        """Convert message to JSON"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON"""
        data = json.loads(json_str)
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def format_time(self) -> str:
        """Format timestamp for display"""
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%H:%M:%S")


class MessageHandler:
    """Handles message encoding/decoding"""
    
    @staticmethod
    def create_message(sender: str, content: str, msg_type: str = "text", 
                       metadata: Optional[Dict] = None) -> Message:
        """Create a new message"""
        return Message(
            sender=sender,
            content=content,
            timestamp=time.time(),
            message_type=msg_type,
            metadata=metadata
        )
    
    @staticmethod
    def encode_message(message: Message) -> bytes:
        """Encode message for transmission"""
        json_str = message.to_json()
        return json_str.encode('utf-8')
    
    @staticmethod
    def decode_message(data: bytes) -> Optional[Message]:
        """Decode received message"""
        try:
            json_str = data.decode('utf-8')
            return Message.from_json(json_str)
        except Exception as e:
            print(f"Error decoding message: {e}")
            return None