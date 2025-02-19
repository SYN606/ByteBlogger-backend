 ByteBlogger Backend

ByteBlogger Backend
===================

The backend component of the ByteBlogger platform, developed using Python and Django, provides robust APIs and handles data management for the application.

Features
--------

*   User authentication and authorization
*   Blog post creation, editing, and deletion
*   Commenting system
*   Category and tag management
*   RESTful API endpoints for seamless frontend integration

Project Structure
-----------------

ByteBlogger-backend/
├── ByteBlogger/
│   ├── \_\_init\_\_.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog/
│   ├── migrations/
│   ├── \_\_init\_\_.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── users/
│   ├── migrations/
│   ├── \_\_init\_\_.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── manage.py
└── requirements.txt
    

Installation
------------

1.  Clone the repository:
    
        git clone https://github.com/SYN606/ByteBlogger-backend.git
    
2.  Navigate to the project directory:
    
        cd ByteBlogger-backend
    
3.  Create and activate a virtual environment:
    
        python -m venv env
        source env/bin/activate  # On Windows, use `env\Scripts\activate`
    
4.  Install the required dependencies:
    
        pip install -r requirements.txt
    
5.  Apply migrations to set up the database:
    
        python manage.py migrate
    
6.  Create a superuser account:
    
        python manage.py createsuperuser
    
7.  Start the development server:
    
        python manage.py runserver
    

Usage
-----

After starting the development server, the API endpoints will be accessible at `http://127.0.0.1:8000/`. You can log in to the Django admin panel at `http://127.0.0.1:8000/admin/` using the superuser credentials created earlier.

Contributing
------------

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for more details.