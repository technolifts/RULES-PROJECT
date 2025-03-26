# DocSecure

A secure document management system built with FastAPI and Next.js.

## Project Overview

DocSecure is a document management system designed with security in mind. It allows users to securely upload, store, share, and manage documents with comprehensive audit logging of all user actions.

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **Document Management**: Upload, view, and delete documents
- **Document Sharing**: Generate secure share links with expiration dates
- **Audit Logging**: Comprehensive logging of all user actions
- **Security**: Input validation, secure file handling, and proper authorization checks

## Tech Stack

- **Frontend**: Next.js with React and TypeScript
- **Backend**: Python with FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT-based with username/password
- **Storage**: Local file system
- **Deployment**: Docker containers

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/docsecure.git
   cd docsecure
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
docsecure/
├── backend/                # FastAPI backend
│   ├── alembic/            # Database migrations
│   ├── app/                # Application code
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Utility functions
│   └── tests/              # Backend tests
└── frontend/               # Next.js frontend
    ├── app/                # Next.js app router
    ├── components/         # React components
    ├── contexts/           # React contexts
    └── tests/              # Frontend tests
```

## API Endpoints

- **Authentication**:
  - POST `/register`: Register a new user
  - POST `/token`: Login and get access token

- **Documents**:
  - GET `/documents/`: List user's documents
  - POST `/documents/`: Upload a new document
  - GET `/documents/{id}`: Get document details
  - DELETE `/documents/{id}`: Delete a document

- **Shares**:
  - GET `/shares/`: List user's share links
  - POST `/shares/`: Create a new share link
  - DELETE `/shares/{id}`: Delete a share link
  - GET `/public/documents/{token}`: Get shared document info
  - GET `/public/documents/{token}/download`: Download shared document

- **Audit Logs**:
  - GET `/audit-logs/`: Get audit logs with filtering options

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Input validation and sanitization
- Secure file handling
- Proper authorization checks
- Comprehensive audit logging
- Rate limiting
- CORS configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.
