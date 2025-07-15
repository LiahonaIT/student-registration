# config.py
import os

class Config:
    # Secret key for session signing and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///registration.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload folders
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SIGNATURE_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'signatures')
    IMMUNIZATION_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'immunizations')

    # Maximum file upload size (e.g., 2MB)
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    # Allowed extensions for file uploads
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = os.environ.get(
        'ADMIN_PASSWORD_HASH',
        'scrypt:32768:8:1$Ehq0FqfrcHh9dExD$27ea9334e35348037337b7fcefd79a5b0b9394f0eddb36ee066c5a720f2d0fd84e3a0642a0e7b5fb0e9f7fc92f02078aa9766d9d320926f25fa42f553d7b2e5b'
    )
