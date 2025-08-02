# Cursor IDE Integration

This document describes the Cursor IDE integration feature that allows users to send prompts directly to Cursor IDE from the Prompt Manager.

## Overview

The Cursor IDE integration provides a seamless way to send prompts from the Prompt Manager to Cursor IDE's active chat. This feature supports both individual prompts and merged prompts.

## Features

### 1. Send Individual Prompts
- Send any prompt from the prompt view page to Cursor IDE
- Automatic clipboard copying with formatted content
- File opening in Cursor IDE (if available)

### 2. Send Merged Prompts
- Send merged prompts from the merge result page
- Maintains the merged structure and formatting
- Includes metadata about the merge operation

### 3. Multiple Delivery Methods
- **Clipboard Method**: Copy prompt to system clipboard
- **File Method**: Open prompt as a temporary file in Cursor IDE

## How It Works

### 1. Cursor Detection
The system automatically detects if Cursor IDE is installed by checking common installation paths:

**Windows:**
- `C:\Users\{username}\AppData\Local\Programs\Cursor\Cursor.exe`
- `C:\Program Files\Cursor\Cursor.exe`
- `C:\Program Files (x86)\Cursor\Cursor.exe`

**macOS:**
- `/Applications/Cursor.app/Contents/MacOS/Cursor`

**Linux:**
- `/usr/bin/cursor`
- `/opt/cursor/cursor`
- `~/.local/bin/cursor`

### 2. Content Formatting
Prompts are formatted with:
- Title as a markdown header (`# Title`)
- Content with proper line breaks
- Metadata for merged prompts

### 3. Delivery Process
1. User clicks "Send to Cursor" button
2. System checks Cursor IDE availability
3. Content is formatted and sent via selected method
4. User receives instructions for next steps

## API Endpoints

### GET /api/cursor/status
Check Cursor IDE availability and capabilities.

**Response:**
```json
{
  "available": true,
  "executable_path": "/path/to/cursor",
  "platform": "nt",
  "capabilities": {
    "send_to_chat": true,
    "open_files": true,
    "api_integration": false
  }
}
```

### POST /api/cursor/send
Send prompt content to Cursor IDE.

**Request Body:**
```json
{
  "content": "Prompt content here",
  "title": "Optional title",
  "method": "clipboard" // or "file"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Prompt copied to clipboard!",
  "instructions": [
    "1. Open Cursor IDE",
    "2. Navigate to the active chat",
    "3. Paste the content (Ctrl+V / Cmd+V)",
    "4. Press Enter to send the prompt"
  ],
  "content": "Formatted content"
}
```

### POST /api/cursor/send/{prompt_id}
Send a specific prompt by ID to Cursor IDE.

**Query Parameters:**
- `method`: "clipboard" or "file" (default: "clipboard")

## User Interface

### Button Locations
1. **Individual Prompt View**: "Send to Cursor" button in the action bar
2. **Merge Result Page**: "Send to Cursor" button in the actions section

### Modal Dialog
When clicking "Send to Cursor", a modal dialog appears with:
- Cursor IDE availability status
- Method selection (clipboard vs file)
- Step-by-step instructions
- Success/error feedback

## Installation Requirements

### Python Dependencies
```bash
pip install pyperclip
# For Windows
pip install pywin32
```

### System Requirements
- Cursor IDE installed (optional, fallback to manual copy)
- Clipboard access permissions
- File system write permissions (for temporary files)

## Error Handling

### Cursor Not Found
- Shows warning message
- Provides manual copy option
- Continues to work with clipboard fallback

### Clipboard Access Issues
- Falls back to manual copy instructions
- Shows formatted content for manual copying
- Provides clear error messages

### File System Issues
- Graceful degradation to clipboard method
- Temporary file cleanup on errors
- User-friendly error messages

## Security Considerations

### Temporary Files
- Files are created with secure permissions
- Automatic cleanup after use
- No sensitive data persistence

### Clipboard Access
- Uses system clipboard APIs
- No data transmission to external services
- Local-only operation

## Troubleshooting

### Common Issues

1. **Cursor not detected**
   - Verify Cursor IDE installation
   - Check if executable is in PATH
   - Try manual copy method

2. **Clipboard not working**
   - Check browser permissions
   - Try file method instead
   - Use manual copy option

3. **File method fails**
   - Verify Cursor IDE is running
   - Check file system permissions
   - Try clipboard method instead

### Debug Information
Run the test script to check system status:
```bash
python test_cursor_integration.py
```

## Future Enhancements

### Planned Features
1. **Direct API Integration**: Direct communication with Cursor IDE
2. **Chat History**: Track sent prompts and responses
3. **Template Support**: Custom formatting templates
4. **Batch Operations**: Send multiple prompts at once

### Technical Improvements
1. **Better Cursor Detection**: More robust path detection
2. **Cross-Platform Clipboard**: Improved clipboard handling
3. **Error Recovery**: Better error handling and recovery
4. **Performance**: Optimized file operations

## Contributing

To contribute to the Cursor IDE integration:

1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation
4. Test on multiple platforms
5. Consider security implications

## Support

For issues with Cursor IDE integration:
1. Check the troubleshooting section
2. Run the test script
3. Review error messages
4. Check system requirements
5. Report issues with debug information 