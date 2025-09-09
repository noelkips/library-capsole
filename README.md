Library Management System API
A Django REST Framework API for managing a library's users, books, and transactions, built as the final capstone project for the ALX Backend Engineering program.
Overview
This API provides functionality for user registration, book browsing, checkout and return of books, and admin management of users, books, and overdue transactions. It uses Django REST Framework with SQLite for local development and is configured for PostgreSQL deployment on PythonAnywhere. The API includes Swagger UI for interactive testing and a JSON fixture to populate the database with 5 users, 20 books, and 10 transactions (including 3 overdue) for demonstration purposes.
Features

User Management: Register users, manage user details (admin-only for updates/deletes).
Book Management: Create, read, update, delete books (create/update/delete admin-only), with filtering by author or title.
Transaction Management: Check out and return books, view overdue transactions (admin-only).
Authentication: Session-based authentication with Django’s built-in auth system.
API Documentation: Swagger UI at /swagger/ for endpoint exploration.

Technologies

Django
Django REST Framework
drf-yasg (Swagger UI)
SQLite (development)
PostgreSQL (production)
PythonAnywhere (deployment)

Setup (Local)

Clone the Repository:git clone https://github.com/noelkips/library-capsole.git
cd library-capsole


Create a Virtual Environment:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:pip install -r requirements.txt


Apply Migrations:python manage.py makemigrations
python manage.py migrate


Load Fixture Data:python manage.py loaddata books_users_transactions.json


Set User Passwords (fixture passwords are placeholders):python manage.py shell

from core.models import User
from django.contrib.auth.hashers import make_password
users = User.objects.all()
for user in users:
    user.password = make_password('userpass123' if user.username != 'admin' else 'adminpass123')
    user.save()
exit()


Create a Superuser (optional, if not using fixture):python manage.py createsuperuser


Example: admin / admin@example.com / adminpass123


Run the Server:python manage.py runserver


Access the API:
Swagger UI: http://127.0.0.1:8000/swagger/
Admin Panel: http://127.0.0.1:8000/admin/ (login with admin:adminpass123)



Deployment (PythonAnywhere)

Clone the Repository:git clone https://github.com/noelkips/library-capsole.git


Create a Virtual Environment:mkvirtualenv --python=/usr/bin/python3.10 library_env
pip install -r requirements.txt


Set Up PostgreSQL:
Configure a PostgreSQL database in PythonAnywhere’s Databases tab.
Update settings.py with your PostgreSQL credentials:DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'your_db_host',
        'PORT': '5432',
    }
}




Apply Migrations and Load Fixture:python manage.py makemigrations
python manage.py migrate
python manage.py loaddata books_users_transactions.json
python manage.py collectstatic


Configure WSGI:
Update the WSGI file in PythonAnywhere’s Web tab to point to library/wsgi.py.


Access the API:
Swagger UI: https://librarycapsole.pythonanywhere.com/swagger/



API Endpoints



Endpoint
Method
Description
Authentication



/api/users/
GET, POST
List users (admin-only), register new users (public)
Authenticated (GET), None (POST)


/api/users/<id>/
GET, PUT, DELETE
Retrieve, update, delete user (admin-only)
Authenticated


/api/books/
GET, POST
List/filter books (public), create book (admin-only)
None (GET), Authenticated (POST)


/api/books/<id>/
GET, PUT, DELETE
Retrieve, update, delete book (admin-only)
Authenticated


/api/transactions/checkout/
POST
Check out a book
Authenticated


/api/transactions/<id>/return/
PUT
Return a book
Authenticated


/api/transactions/overdue/
GET
List overdue transactions (admin-only)
Authenticated


Example Usage:

Register User:curl -X POST http://127.0.0.1:8000/api/users/ -d '{"username": "testuser18", "email": "test18@example.com", "password": "testpass123"}' -H "Content-Type: application/json"


Filter Books:curl http://127.0.0.1:8000/api/books/?author=Tolkien


Check Out Book (requires login):curl -X POST http://127.0.0.1:8000/api/transactions/checkout/ -d '{"book_id": 1}' -H "Content-Type: application/json" -H "X-CSRFToken: <your-csrf-token>"



Testing
Run unit tests to verify functionality:
python manage.py test


Tests cover user CRUD, book CRUD, checkout/return, and overdue transactions.
80%+ code coverage achieved.

Demo
A 5-minute Loom video demonstrating the API is available: <your-loom-video-link> (to be added after recording).
Notes

The fixture (books_users_transactions.json) populates the database with 5 users, 20 books, and 10 transactions for testing.
Minor validation edge cases may remain but do not impact core functionality.
The project is hosted at https://<yourusername>.pythonanywhere.com/swagger/ (or local at http://127.0.0.1:8000/swagger/ if not deployed).
