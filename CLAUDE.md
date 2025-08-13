# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Excel to WhatsApp bulk messaging application that supports sending messages to thousands of recipients. The application is built with Python using CustomTkinter for the UI and includes advanced features for high-volume message sending with proper rate limiting and error handling.

## Development Commands

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Alternative using Makefile
make install
```

### Running the Application
```bash
# Main application (basic version)
python main.py

# Optimized version for large volumes (10k+ messages)
python main_optimized.py

# Version with advanced progress bars
python main_with_advanced_progress.py
```

### Testing
```bash
# Run individual test files
python test_duplicate_prevention.py
python test_anti_doublon.py
python test_timing_verification.py
python test_interruption_reprise.py
python test_errors_critical.py
python test_ui_robustness.py

# Test using Makefile
make test
```

### Building/Packaging
```bash
# Build with PyInstaller
make build-pyinstaller

# Build with cx_Freeze  
make build-cx-freeze

# Build all formats
make build-all

# Create DMG on macOS
make build-dmg

# Clean build files
make clean
```

## Architecture Overview

### Core Components

1. **Main Applications**:
   - `main.py`: Basic Excel reader with WhatsApp integration
   - `main_optimized.py`: Production version optimized for 10k+ messages with bulk sending
   - `main_with_advanced_progress.py`: Version with enhanced progress tracking UI

2. **API Layer** (`api/`):
   - `whatsapp_client.py`: WhatsApp API client with rate limiting and threading support
   - `bulk_sender.py`: Specialized bulk message sender with session persistence, batch processing, and memory management

3. **Configuration** (`config/`):
   - `config_manager.py`: Secure configuration management with encryption
   - `security.py`: Security utilities for sensitive data handling

4. **UI Components** (`ui/`):
   - `bulk_send_dialog.py`: Specialized dialog for high-volume sending
   - `components.py`: Reusable UI components
   - `progress_widgets.py`: Advanced progress tracking widgets
   - `sent_numbers_dialog.py`: Dialog for viewing sent message history

5. **Utilities** (`utils/`):
   - `logger.py`: Structured logging system
   - `validators.py`: Phone number and data validation
   - `exceptions.py`: Custom exception classes

### Key Features

- **Bulk Messaging**: Optimized for 10k+ messages with batch processing (50 messages per batch)
- **Session Persistence**: Ability to resume sending after interruption
- **Rate Limiting**: Intelligent rate limiting to prevent API blocking (configurable)
- **Memory Management**: Automatic garbage collection every 100 messages
- **Threading Control**: Limited to 1-3 concurrent threads to prevent overload
- **Secure Configuration**: Encrypted storage of API tokens and instance IDs
- **Progress Tracking**: Real-time progress bars with ETA and statistics

### Configuration

The app uses UltraMsg API for WhatsApp messaging. Configuration is stored securely in:
- `~/.excel_whatsapp/config.json` (encrypted sensitive data)
- `~/.excel_whatsapp/sessions/` (sending session persistence)
- `~/.excel_whatsapp/logs/` (application logs)

### Performance Optimizations

For high-volume sending (10k+ messages):
- Batch size: 50 messages
- Max workers: 1-3 threads
- Batch delay: 2-5 seconds
- Rate limit: 0.8 messages/second
- Memory cleanup: Every 100 messages
- Retry attempts: 2-3 with exponential backoff

### Development Notes

- The codebase uses French comments and variable names
- Three main versions exist for different use cases
- CustomTkinter is used for modern dark-themed UI
- Pandas handles Excel file processing
- Extensive testing suite covers duplicate prevention, timing, and robustness
- All sensitive data (API tokens) is encrypted using the security module