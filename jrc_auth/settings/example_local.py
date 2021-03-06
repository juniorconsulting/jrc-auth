import os

from jrc_auth.settings.base import BASE_DIR


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'
        'NAME': 'mydb',  # Or path to database file if using sqlite3 (db.sqlite3)
        # The following settings are not used with sqlite3:
        'USER': 'myuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, '../collected-static')

# Email setup prod
ANYMAIL = {
    "MAILGUN_API_KEY": "<your Mailgun key>",
}
EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"  # or sendgrid.SendGridBackend, or...
DEFAULT_FROM_EMAIL = "you@example.com"  # if you don't already have this in settings

