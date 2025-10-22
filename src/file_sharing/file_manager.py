from typing import List, Dict
import threading
from .file_transfer import FileMetadata


class FileManager:
    """Manages file transfer sessions"""
    
    def __init__(self):
        self.active_transfers: Dict[str, Dict] = {}
        self.completed_transfers: List[FileMetadata] = []
        self.lock = threading.Lock()
        
    def start_transfer(self, transfer_id: str, metadata: FileMetadata):
        """Register new file transfer"""
        with self.lock:
            self.active_transfers[transfer_id] = {
                'metadata': metadata,
                'progress': 0,
                'status': 'in_progress'
            }
    
    def update_progress(self, transfer_id: str, bytes_transferred: int, total_bytes: int):
        """Update transfer progress"""
        with self.lock:
            if transfer_id in self.active_transfers:
                progress = (bytes_transferred / total_bytes) * 100
                self.active_transfers[transfer_id]['progress'] = progress
    
    def complete_transfer(self, transfer_id: str, success: bool):
        """Mark transfer as complete"""
        with self.lock:
            if transfer_id in self.active_transfers:
                transfer = self.active_transfers.pop(transfer_id)
                transfer['status'] = 'completed' if success else 'failed'
                
                if success:
                    self.completed_transfers.append(transfer['metadata'])
    
    def get_active_transfers(self) -> List[Dict]:
        """Get list of active transfers"""
        with self.lock:
            return list(self.active_transfers.values())
    
    def get_completed_transfers(self) -> List[FileMetadata]:
        """Get list of completed transfers"""
        with self.lock:
            return self.completed_transfers.copy()
    
    def clear_history(self):
        """Clear completed transfers history"""
        with self.lock:
            self.completed_transfers.clear()
