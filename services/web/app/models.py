import pyotp
from flask_sqlalchemy import SQLAlchemy
from passlib.handlers.bcrypt import bcrypt
from flask_login import UserMixin
from sqlalchemy import func

from services.web.app.extensions.db import db

db: SQLAlchemy


class Servers(db.Model):
    __tablename__ = "servers"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(32))
    ipv4 = db.Column(db.String(15))
    ipv6 = db.Column(db.String(39))
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32))
    email = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # Store hashed passwords
    pyotp_secret = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    is_two_factor_authentication_enabled = db.Column(db.Boolean(), default=True)

    def __init__(self, email, password, username=None):
        self.email = email
        self.password_hash = self.hash_password(password)  # Hash password before storing
        self.username = username if username is not None else ""
        self.pyotp_secret = ""
        self.is_two_factor_authentication_enabled = True

    def is_otp_valid(self, user_otp):
        # totp = pyotp.parse_uri(self.get_authentication_setup_uri())
        totp = pyotp.TOTP(self.pyotp_secret)
        print(totp.now())
        print(user_otp)
        return totp.verify(user_otp)

    def generate_otp_token(self, interval=200):
        # Generates a TOTP token based on the given secret and interval
        totp = pyotp.TOTP(self.pyotp_secret, interval=interval)
        return totp.now()

    def regenerate_pyotp_secret(self):
        self.pyotp_secret = pyotp.random_base32()
        db.session.commit()

    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt."""
        return bcrypt.hash(password)

    def verify_password(self, password):
        """Verify a password against the stored hash."""
        return bcrypt.verify(password, self.password_hash)


class LiveStatus(db.Model):
    __tablename__ = 'status_live'

    id = db.Column(db.Integer(), primary_key=True)
    stream_name = db.Column(db.String(255), nullable=False)
    last_start = db.Column(db.Integer())
    last_stop = db.Column(db.Integer())
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)

    def __init__(self, stream_name, last_start=None, last_stop=None):
        self.stream_name = stream_name
        self.last_start = last_start if last_start is not None else ""
        self.last_stop = last_stop if last_stop is not None else ""
