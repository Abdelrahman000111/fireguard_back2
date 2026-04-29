import firebase_admin
from firebase_admin import credentials
from django.conf import settings


def initialize_firebase():
    """
    Call this once at Django startup via AppConfig.ready().
    Safe to call multiple times — checks if already initialized.
    """
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            print("[Firebase] Initialized successfully.")
        except Exception as e:
            print(f"[Firebase] Initialization failed: {e}")