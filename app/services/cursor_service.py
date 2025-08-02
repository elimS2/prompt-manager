"""
Service for Cursor IDE integration.
Handles communication with Cursor IDE for sending prompts to active chat.
"""
import json
import os
import subprocess
import tempfile
import time
from typing import Dict, Optional, List
from app.utils.logging import get_logger

logger = get_logger(__name__)


class CursorService:
    """Service for integrating with Cursor IDE."""
    
    def __init__(self):
        self.cursor_executable = self._find_cursor_executable()
        self.logger = logger
        self.temp_files = []  # Track temporary files for cleanup
    
    def _find_cursor_executable(self) -> Optional[str]:
        """Find Cursor IDE executable path."""
        possible_paths = [
            # Windows paths
            r"C:\Users\{}\AppData\Local\Programs\Cursor\Cursor.exe".format(os.getenv('USERNAME', '')),
            r"C:\Program Files\Cursor\Cursor.exe",
            r"C:\Program Files (x86)\Cursor\Cursor.exe",
            
            # macOS paths
            "/Applications/Cursor.app/Contents/MacOS/Cursor",
            
            # Linux paths
            "/usr/bin/cursor",
            "/opt/cursor/cursor",
            os.path.expanduser("~/.local/bin/cursor"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(['where', 'cursor'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def is_cursor_available(self) -> bool:
        """Check if Cursor IDE is available on the system."""
        return self.cursor_executable is not None
    
    def send_prompt_to_cursor(self, prompt_content: str, prompt_title: str = None) -> Dict:
        """
        Send prompt content to Cursor IDE active chat.
        
        Args:
            prompt_content: The prompt content to send
            prompt_title: Optional title for the prompt
            
        Returns:
            Dict with success status and message
        """
        if not self.is_cursor_available():
            return {
                'success': False,
                'message': 'Cursor IDE not found. Please ensure Cursor is installed and accessible.'
            }
        
        try:
            # Create a temporary file with the prompt content
            # Use a more descriptive filename and keep it longer
            timestamp = int(time.time())
            filename = f"prompt_{timestamp}.txt"
            
            # Create temp file in a more accessible location
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, filename)
            
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                # Add title if provided
                if prompt_title:
                    f.write(f"# {prompt_title}\n\n")
                
                f.write(prompt_content)
            
            # Track the file for later cleanup
            self.temp_files.append(temp_file_path)
            
            # Try to open the file in Cursor
            result = self._open_in_cursor(temp_file_path, prompt_content, prompt_title)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending prompt to Cursor: {str(e)}")
            return {
                'success': False,
                'message': f'Error sending prompt to Cursor: {str(e)}'
            }
    
    def _open_in_cursor(self, file_path: str, content: str, title: str = None) -> Dict:
        """
        Open content in Cursor IDE.
        
        Args:
            file_path: Path to temporary file
            content: The prompt content
            title: Optional title for the prompt
            
        Returns:
            Dict with success status and instructions
        """
        try:
            # Try to open the file in Cursor
            process = subprocess.Popen([self.cursor_executable, file_path], 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            
            # Wait a moment to see if the process starts successfully
            time.sleep(0.5)
            
            if process.poll() is None:  # Process is still running
                return {
                    'success': True,
                    'message': 'Prompt opened in Cursor IDE successfully!',
                    'content': content,
                    'file_path': file_path,
                    'instructions': [
                        '1. The prompt has been opened in Cursor IDE',
                        '2. Copy the content from the opened file',
                        '3. Paste it into the active Cursor chat',
                        '4. Press Enter to send the prompt',
                        '5. You can close the file when done'
                    ]
                }
            else:
                # Process failed to start
                return {
                    'success': False,
                    'message': 'Failed to open Cursor IDE. Please try the clipboard method instead.',
                    'content': content,
                    'instructions': [
                        '1. Copy the prompt content below',
                        '2. Open Cursor IDE manually',
                        '3. Navigate to the active chat',
                        '4. Paste the content and press Enter'
                    ]
                }
            
        except Exception as e:
            self.logger.error(f"Error opening file in Cursor: {str(e)}")
            return {
                'success': False,
                'message': f'Error opening Cursor IDE: {str(e)}',
                'content': content,
                'instructions': [
                    '1. Copy the prompt content below',
                    '2. Open Cursor IDE manually',
                    '3. Navigate to the active chat',
                    '4. Paste the content and press Enter'
                ]
            }
    
    def get_cursor_status(self) -> Dict:
        """
        Get Cursor IDE status and capabilities.
        
        Returns:
            Dict with Cursor status information
        """
        return {
            'available': self.is_cursor_available(),
            'executable_path': self.cursor_executable,
            'platform': os.name,
            'capabilities': {
                'send_to_chat': self.is_cursor_available(),
                'open_files': self.is_cursor_available(),
                'api_integration': False  # Future enhancement
            }
        }
    
    def copy_to_clipboard_with_instructions(self, content: str, title: str = None) -> Dict:
        """
        Copy content to clipboard with instructions for Cursor.
        
        Args:
            content: The prompt content
            title: Optional title for the prompt
            
        Returns:
            Dict with success status and instructions
        """
        try:
            # Format the content for clipboard
            formatted_content = content
            if title:
                formatted_content = f"# {title}\n\n{content}"
            
            # Try to copy to clipboard using different methods
            clipboard_success = self._copy_to_clipboard(formatted_content)
            
            if clipboard_success:
                return {
                    'success': True,
                    'message': 'Prompt copied to clipboard successfully!',
                    'instructions': [
                        '1. Open Cursor IDE',
                        '2. Navigate to the active chat',
                        '3. Paste the content (Ctrl+V / Cmd+V)',
                        '4. Press Enter to send the prompt'
                    ],
                    'content': formatted_content
                }
            else:
                return {
                    'success': False,
                    'message': 'Could not copy to clipboard automatically.',
                    'instructions': [
                        '1. Manually copy the prompt content below',
                        '2. Open Cursor IDE',
                        '3. Navigate to the active chat',
                        '4. Paste the content and press Enter'
                    ],
                    'content': formatted_content
                }
                
        except Exception as e:
            self.logger.error(f"Error copying to clipboard: {str(e)}")
            return {
                'success': False,
                'message': f'Error copying to clipboard: {str(e)}',
                'content': content
            }
    
    def _copy_to_clipboard(self, content: str) -> bool:
        """
        Copy content to system clipboard.
        
        Args:
            content: The content to copy
            
        Returns:
            True if successful, False otherwise
        """
        # Try multiple methods in order of preference
        methods = [
            self._try_pyperclip,
            self._try_win32clipboard,
            self._try_xclip
        ]
        
        for method in methods:
            try:
                if method(content):
                    return True
            except Exception as e:
                self.logger.debug(f"Clipboard method {method.__name__} failed: {e}")
                continue
        
        return False
    
    def _try_pyperclip(self, content: str) -> bool:
        """Try copying using pyperclip."""
        import pyperclip
        pyperclip.copy(content)
        return True
    
    def _try_win32clipboard(self, content: str) -> bool:
        """Try copying using win32clipboard (Windows only)."""
        if os.name != 'nt':
            return False
        
        import win32clipboard
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(content)
        win32clipboard.CloseClipboard()
        return True
    
    def _try_xclip(self, content: str) -> bool:
        """Try copying using xclip (Unix-like systems only)."""
        if os.name == 'nt':
            return False
        
        import subprocess
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                 stdin=subprocess.PIPE)
        process.communicate(input=content.encode('utf-8'))
        return process.returncode == 0
    
    def cleanup_temp_files(self):
        """Clean up temporary files created by this service."""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                self.logger.warning(f"Could not delete temp file {file_path}: {e}")
        
        self.temp_files.clear() 