# AI-Powered FAQ Bot API

A lightweight, AI-powered API built with FastAPI to automate responses to frequently asked questions. Designed for multi-organization use, it provides a scalable backend for intelligent FAQ bots.

---

## Project Status

This project is under active development.

#### ✅ Implemented

- **Core Infrastructure**:
  - FastAPI application structure.
  - Asynchronous PostgreSQL database connection using `asyncpg`.
  - `SQLModel` ORM setup with Alembic for migrations.
  - Environment-based configuration using `.env` files and Pydantic.
- **Features & Endpoints**:
  - `User` and `Organization` database models.
  - User authentication with JWT.
  - Password hashing using `passlib`.
  - API endpoints for user registration, login, and organization management.
  - Interactive API documentation with Scalar.
  - Document upload, replace, list, download, and delete endpoints.
  - AWS S3 integration for file storage (see utils/s3.py).

#### 🚧 Planned

- **Core Features**:
  - **Document Handling**: Upload, process, and chunk FAQ documents.
  - **AI Embeddings**: Generate vector embeddings for document chunks using the OpenAI API.
  - **Vector Search**: Implement similarity search using **Qdrant** or **PostgreSQL pgvector** to find the most relevant answers.
- **API Endpoints**:
  - `/documents` for managing uploaded files.
  - `/ask` to submit a question and receive an AI-powered answer.
  - Admin endpoints for managing organization-specific FAQs.
- **Frontend**:
  - An optional chatbot interface to interact with the API.

---

## Getting Started

- All document files are stored securely in AWS S3. Access is managed via API endpoints and AWS credentials in your .env file.

Follow these instructions to set up and run the project on your local machine.

### 1. Prerequisites

- Python
- PostgreSQL server

### 2. Clone the Repository

```bash
git clone https://github.com/Kasayka1999/AI-Powered-FAQ-Bot-API.git
cd AI-Powered-FAQ-Bot-API
```

### 3. Set Up Environment

Create a virtual environment to manage dependencies:

```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

This project uses a `.env` file for configuration. Since this file is ignored by Git, you need to create your own.

Create a file named `.env` in the project root. You can copy the example structure below.

```dotenv
# .env

# PostgreSQL Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db

# JWT Settings
JWT_SECRET=a-strong-random-secret-key
JWT_ALGORITHM=HS256
JWT_TOKEN_EXPIRE_MINUTES=30

# AWS S3 credentials
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_server_region
AWS_S3_BUCKET=your_bucket

# OpenAI API Key (for planned embedding feature)
# OPENAI_API_KEY="your-openai-api-key"
```

**Create your `.env` file and fill in your actual database credentials and a secure secret key.**

### 5. Set Up the Database

Run the database migrations to create the necessary tables:

```bash
alembic upgrade head
```

### 6. Run the Application

Once your `.env` file is configured, you can run the FastAPI server from the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/scalar`.

---

## Project Structure

A brief overview of the key directories in this project:

```
.
├── migrations/           # Database migration scripts
├── app/                  # Main application source code
│   ├── api/              # API logic
│   │   ├── dependencies.py # API dependencies (e.g., get_current_user, SessionDep)
│   │   └── v1/           # API version 1
│   │       ├── routers/  # Specific endpoint files
│   │       └── router.py # Main v1 router aggregation
│   ├── database/         # Database session management
│   ├── models/           # SQLModel table definitions and schemas
│   ├── utils/            # Utility functions (hashing, JWT, AWS S3)
│   ├── config.py         # Environment-based configuration
│   └── main.py           # FastAPI app entry point
├── alembic.ini           # Alembic configuration
└── README.md
```

---

## API Endpoints

#### Available Endpoints

- `POST /dashboard/signup` - Create a new user.
- `POST /dashboard/login` - Log in to get an access token.
- `GET /dashboard/users/me/` - Get current user's information.
- `POST /organization/create` - Create a new organization.
- `DELETE /organization/delete/` - Delete an organization.
- `POST /documents/upload`     # Upload or replace a document (PDF/TXT) to S3
- `GET /documents/my_documents` # List all documents for the current organization
- `POST /documents/download`    # Download a document from S3
- `DELETE /documents/delete`    # Delete a document from S3 and database (with confirmation)

#### Planned Features & Endpoints

The next development phase will focus on implementing the core AI and document-handling capabilities:

- **Document Management**: Endpoints for uploading, processing, and managing FAQ documents within a specific organization.
- **AI-Powered Q&A**: A primary endpoint to accept a user's question and return a contextually relevant answer derived from the organization's documents.
- **Analytics & Logging**: Endpoints for administrators to retrieve logs and gain insights into bot interactions and performance.

---

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Kasayka1999/AI-Powered-FAQ-Bot-API/issues).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.