# Prompt Manager

A modern Flask-based application for managing, organizing, and merging text prompts. Built with clean architecture principles, following SOLID, DRY, KISS, and other software engineering best practices.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### Core Functionality
- **CRUD Operations**: Create, read, update, and delete prompts with ease
- **Tag System**: Organize prompts with a flexible tagging system
- **Search & Filter**: Powerful search across titles, content, and descriptions
- **Merge Prompts**: Multiple merge strategies for combining prompts:
  - Simple concatenation
  - Custom separators
  - Numbered lists
  - Bulleted lists
  - Template-based merging

### User Experience
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Enhanced Prompt List**: View and copy content directly from the list without navigation
- **Inline Content Preview**: Expandable content with smooth animations
- **Quick Copy Functionality**: One-click copying with visual feedback
- **Keyboard Shortcuts**: Ctrl+K for search, Ctrl+N for new prompt, Escape to close previews
- **Toast Notifications**: Non-intrusive feedback for user actions
- **Auto-save Drafts**: Never lose your work (coming soon)

### Technical Features
- **RESTful API**: Complete API for programmatic access
- **Soft Delete**: Safely delete prompts with recovery option
- **Pagination**: Efficient handling of large datasets
- **Type Safety**: Full type hints throughout the codebase
- **Test Coverage**: Comprehensive unit and integration tests

### IDE Integration
- **Cursor IDE Integration**: Send prompts directly to Cursor IDE's active chat
- **Multiple Delivery Methods**: Clipboard copying and file opening
- **Automatic Detection**: Detects Cursor IDE installation automatically
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🛠️ Installation

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd prompt-manager
```

2. **Set up development environment**
```bash
make dev-setup
```

This command will:
- Create a virtual environment
- Install all dependencies
- Initialize the database
- Seed sample data

### Manual Installation

1. **Create and activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements-dev.txt
```

3. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configurations
```

4. **Initialize database**
```bash
python scripts/init_db.py
python scripts/seed_data.py  # Optional: add sample data
```

## 🏃 Running the Application

### Development Server
```bash
make run
# Or directly: python run.py
```

The application will be available at `http://localhost:5001`

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 wsgi:app

# Using Docker (coming soon)
docker-compose up
```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Run Specific Test Types
```bash
make test-unit        # Unit tests only
make test-integration # Integration tests only
make coverage        # Generate coverage report
```

### Code Quality Checks
```bash
make lint       # Run flake8 linting
make format     # Format code with black
make type-check # Run mypy type checking
make check      # Run all checks
```

## 📁 Project Structure

```
prompt-manager/
├── app/
│   ├── __init__.py         # Application factory
│   ├── models/             # Domain models (Prompt, Tag)
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic layer
│   ├── controllers/        # HTTP request handlers
│   ├── static/             # CSS, JavaScript, images
│   ├── templates/          # Jinja2 HTML templates
│   └── utils/              # Helper functions
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Test fixtures
├── config/                 # Configuration modules
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── migrations/             # Database migrations
```

## 🏗️ Architecture

The project follows a **clean architecture** pattern with clear separation of concerns:

### Layers
1. **Models**: Domain entities with business rules
2. **Repositories**: Abstract data access, implements Repository pattern
3. **Services**: Business logic, orchestrates operations
4. **Controllers**: Handle HTTP requests/responses
5. **Templates**: Presentation layer with Jinja2

### Design Patterns
- **Repository Pattern**: Abstraction over data access
- **Service Layer**: Encapsulates business logic
- **Factory Pattern**: Application factory for different environments
- **MVC Pattern**: Clear separation of concerns

### Principles Applied
- **SOLID**: Single responsibility, open/closed, etc.
- **DRY**: Don't repeat yourself
- **KISS**: Keep it simple
- **YAGNI**: You aren't gonna need it

## 🔌 API Documentation

### Authentication
Google OAuth 2.0 is supported for the web app (Flask-Login sessions). API write endpoints are protected.

#### Google OAuth Setup (Development)
1. Create OAuth consent screen in Google Cloud Console (External, Testing).
2. Create OAuth Client ID (Web application):
   - Authorized redirect URIs:
     - `http://localhost:5001/auth/callback`
     - `http://127.0.0.1:5001/auth/callback`
3. Set environment variables in `.env`:
   ```env
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   OAUTH_GOOGLE_REDIRECT_URI=http://localhost:5001/auth/callback
   # Recommended: use instance DB with absolute path
   DATABASE_URL=sqlite:///C:/path/to/project/instance/prompt_manager.db
   ```
4. Apply migrations to the active DB:
   ```powershell
   venv\Scripts\python -m flask db upgrade
   ```
5. Run the app and click "Sign in with Google".

Troubleshooting:
- If you see `mismatching_state`, ensure you use a single host (localhost or 127.0.0.1) and that cookies are allowed.
- If you see `no such table: users`, verify the active DB URI at startup logs and run migrations against that DB. Use `scripts/db_introspect.py` to inspect tables and alembic version.

### Endpoints

#### Prompts
- `GET /api/prompts` - List prompts with pagination
- `POST /api/prompts` - Create new prompt
- `GET /api/prompts/{id}` - Get single prompt
- `PUT /api/prompts/{id}` - Update prompt
- `DELETE /api/prompts/{id}` - Delete prompt
- `POST /api/prompts/merge` - Merge multiple prompts
- `GET /api/prompts/search` - Search prompts

#### Tags
- `GET /api/tags` - List all tags
- `POST /api/tags` - Create new tag
- `PUT /api/tags/{id}` - Update tag
- `DELETE /api/tags/{id}` - Delete tag
- `GET /api/tags/statistics` - Get tag usage statistics

### Example API Usage

```python
import requests

# Create a prompt
response = requests.post('http://localhost:5001/api/prompts', json={
    'title': 'My Prompt',
    'content': 'This is the prompt content',
    'tags': ['python', 'api']
})

# Search prompts
response = requests.get('http://localhost:5001/api/prompts/search?q=python')
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guide
- Add type hints to new code
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-described

### Code Style
```bash
# Format code before committing
make format

# Run all quality checks
make check
```

## 🐛 Troubleshooting

### Common Issues

1. **Database errors**
   ```bash
   # Reset database
   rm prompt_manager.db
   make init-db seed-db
   ```

2. **Import errors**
   ```bash
   # Ensure virtual environment is activated
   # Reinstall dependencies
   pip install -r requirements-dev.txt
   ```

3. **Port already in use**
   ```bash
   # Change port in .env file
   APP_PORT=5002
   ```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask community for excellent documentation
- Bootstrap team for the UI framework
- All contributors and testers

## 📮 Contact

For questions or support, please [open an issue](https://github.com/yourusername/prompt-manager/issues).

---

Made with ❤️ by the Prompt Manager Team