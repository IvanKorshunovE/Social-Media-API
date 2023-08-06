# Social-Media-API

The Social Media API is a RESTful API for a social media platform. It provides endpoints for user registration, authentication, profile management, post creation and retrieval, social interactions, and more.

## Requirements
- Python 3.x
- Django
- Django REST framework

### How to Run

1. Clone the repository: `git clone https://github.com/IvanKorshunovE/Social-Media-API`
2. Change to the project directory: `cd social-media-api`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install the required packages: `pip install -r requirements.txt`
6. Create a `.env` file by copying the `.env.sample` file and populate it with the required values.
7. Run migrations: `python manage.py migrate`
8. Run the Redis server: `docker run -d -p 6379:6379 redis`
9. Run the Celery worker for task handling: `celery -A social_media_api worker -l INFO`
10. Run Celery beat for task scheduling: `celery -A social_media_api beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`
11. Create a schedule for running sync in the DB.
12. Run the app: `python manage.py runserver`

### API Documentation

The API is well-documented with detailed explanations of each endpoint and their functionalities. The documentation provides sample requests and responses to help you understand how to interact with the API. You can access the API documentation by visiting the following URL in your browser:
- [API Documentation](http://localhost:8000/api/schema/swagger-ui/)
