# FastAPI Library Management System 📚

## **Project Overview**
This Library Management System is developed using **FastAPI** and **SQLModel**, with **MySQL** as the database backend. The system supports **role-based access control**, **JWT authentication**, and **comprehensive API testing using Pytest**. It provides essential features for managing books and user borrowing activities, ensuring a seamless experience for both administrators and library members.

---

## **Project Structure**
```
└── 📁Fast_API_Assignment
    ├── 📁models        # Database models
    ├── 📁routes        # API route definitions
    ├── 📁schemas       # Pydantic schemas for request/response validation
    ├── 📁tests         # Automated test cases using Pytest
    ├── 📁utils         # Utility functions for authentication and security
    ├── .env           # Environment variables
    ├── .gitignore     # Git ignore file
    ├── database.py    # Database connection and session management
    ├── main.py        # Application entry point
    ├── README.md      # Project documentation
    ├── requirements.txt # Project dependencies
```

---

## **Installation & Setup**

### **Step 1: Clone the Repository**
```sh
git clone https://github.com/anuj-consultadd/Fast_API_Assignment.git
cd Fast_API_Assignment
```

### **Step 2: Create & Activate a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **Step 3: Install Dependencies**
```sh
pip install -r requirements.txt
```

### **Step 4: Configure Environment Variables**
Create a `.env` file in the root directory:
```ini
# .env
DATABASE_URL="mysql+pymysql://your_user:your_password@localhost/fastAPI_library_system"
SECRET_KEY="your_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
TEST_DATABASE_URL="mysql+pymysql://your_user:your_password@localhost/TESTING_fastAPI_library_system"
```
🔹 Replace `your_user` and `your_password` with your MySQL credentials.

### **Step 5: Apply Database Migrations**
```sh
alembic upgrade head
```

### **Step 6: Start the FastAPI Server**
```sh
uvicorn app.main:app --reload
```
📌 Open **Swagger UI** at: `http://127.0.0.1:8000/docs`

---

## **Core Features**

### **🔹 Admin Endpoints (Requires Admin Privileges)**
- `POST /admin/books` → Add a new book
- `PUT /admin/books/{id}` → Update book details
- `DELETE /admin/books/{id}` → Delete a book
- `GET /admin/books` → Retrieve all books
- `GET /admin/books/{id}` → Retrieve book details
- `GET /admin/borrowed-books` → View borrowed books

### **🔹 User Endpoints**
- `GET /books` → Browse available books
- `POST /books/{id}/borrow` → Borrow a book
- `POST /books/{id}/return` → Return a borrowed book
- `GET /books/history` → View borrowing history

### **🔹 Authentication & User Management**
- `POST /auth/signup` → Register a new user
- `POST /auth/login` → Obtain access & refresh tokens
- `POST /auth/refresh` → Refresh authentication token
- `POST /auth/logout` → Logout user session
- `GET /auth/me` → Retrieve user details

---

## **Testing & Quality Assurance** 🧪
This project includes automated API testing using **Pytest** to ensure the reliability of endpoints.

### **Run Tests**
```sh
pytest -v
```

### **Pytest Implementation Details**
✔ **Markers** – Categorize and selectively execute test cases.  
✔ **Fixtures** – Reusable setup and teardown logic for tests.  
✔ **Parameterization** – Run tests with multiple data inputs.  
✔ **Assertions** – Validate API responses and expected outcomes.  
✔ **Test Discovery** – Well-organized test structure for automatic detection.  
✔ **Mocking** – Simulate dependencies for isolated testing.


---

