# Task Flow API

Task Flow API is a FastAPI-based project management system that allows users to manage tasks efficiently. It provides endpoints for creating, updating, retrieving, and deleting tasks, with additional features like automatic task cleanup.

## Features

- **Task Management**: Create, update, retrieve, and delete tasks.
- **Automatic Cleanup**: Automatically deletes tasks when their status is set to `done` or when their `due_date` has passed.
- **User Authentication**: Ensures tasks are managed securely by their respective owners.

## Project Structure

```
app/
├── api/
│   ├── routes/
│   │   ├── auth.py       # Authentication routes
│   │   └── task.py       # Task-related routes
│   └── deps.py           # Dependency injection
├── core/
│   ├── config.py         # Configuration settings
│   ├── database.py       # Database setup
│   └── security.py       # Security utilities
├── models/
│   ├── task_model.py     # Task database model
│   └── user_model.py     # User database model
├── schemas/
│   ├── task_schema.py    # Task Pydantic schemas
│   └── user_schema.py    # User Pydantic schemas
├── services/
│   └── task_service.py   # Task business logic
└── main.py               # Application entry point
```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd task-flow
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the FastAPI server:
   ```bash
   cd app
   uvicorn main:app --reload
   ```
2. Open your browser and navigate to:
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to access the interactive API documentation.

## Endpoints

### Task Endpoints

- **Create Task**: `POST /api/tasks/`
- **Get My Tasks**: `GET /api/tasks/`
- **Get Task by ID**: `GET /api/tasks/{id}`
- **Update Task**: `PUT /api/tasks/{id}`
- **Delete Task**: `DELETE /api/tasks/{id}`

### Authentication Endpoints

- **Register User**: `POST /api/auth/register`
  - Registers a new user with a unique username and email.
- **Login**: `POST /api/auth/login`
  - Authenticates a user and returns a JWT token.
- **Get Current User**: `GET /api/auth/me`
  - Retrieves the details of the currently authenticated user.

## Authentication and Authorization

- **Registration**: Users can register with a unique username and email. Passwords are hashed using `bcrypt` before being stored in the database.
- **Login**: Users log in with their username and password. A JWT token is issued upon successful authentication.
- **JWT Authentication**: All protected endpoints require a valid JWT token in the `Authorization` header (e.g., `Bearer <token>`).
- **Authorization**: Tasks are tied to their respective owners. Users can only manage their own tasks. Unauthorized access results in a `401 Unauthorized` error.

## Automatic Cleanup

- Tasks are automatically deleted when:
  - Their status is updated to `done`.
  - Their `due_date` has passed (checked daily by a scheduled task).

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your message here"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.


