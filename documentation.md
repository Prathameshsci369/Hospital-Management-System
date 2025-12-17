# Hospital Management System — Project Documentation

This single-file documentation provides a comprehensive guide to the Hospital Management System (Django project) contained in this repository. It is intended to be uploaded to GitHub as the main documentation for the hospital management application.

---

## Project overview

A Django-based Hospital Management System built with modular apps to handle user accounts, doctors, patients, appointment booking, and Google integration for calendar features. The system includes a modern, responsive UI built with Bootstrap and enhanced with custom CSS/JavaScript. The repository contains both the application code and templates that were redesigned to a contemporary look and feel.

Key points:
- Framework: Django (project was generated using Django 5.2.x)
- Apps (core): `accounts`, `doctors`, `patients`, `appointments`, `google_integration`
- Database (default configured): PostgreSQL (development settings in `settings.py`), but SQLite can be used for quick local testing
- Frontend: Bootstrap 5.x base, Font Awesome icons, Animate.css used for animations. Many templates were enhanced with custom CSS and JS while leaving backend logic untouched.

---

## Features

- User registration and authentication (custom `accounts.User` model)
- Separate flows for doctor and patient registration
- Doctor availability management (add/edit availability slots)
- Appointment booking and confirmation (with animated success UI)
- Doctor & patient dashboards with appointment lists and status badges
- Google OAuth2 integration points (client ID/secret placeholders present)
- Email settings scaffolded for SMTP
- Responsive design and client-side form validation

---

## Quick repository layout

Top-level highlights (relative to repository root):

- `hosptal_management/hospital_system/` — Django project for Hospital Management
  - `manage.py` — Django management script for this project
  - `hospital_system/settings.py` — Django settings (database, installed apps, templates)
  - `hospital_system/urls.py`, `wsgi.py`, `asgi.py`
- `hosptal_management/` — parent folder containing hospital project and `requirements.txt`
- `templates/` — global templates folder used by the project (custom UI templates placed here)
- Other apps and example projects exist elsewhere in the workspace, but the hospital app lives under `hosptal_management/hospital_system`

Note: This repository also contains another Django project (`django_ecommerce` etc.). This documentation focuses on the Hospital Management project located under `hosptal_management/`.

---

## Important files

- `hosptal_management/hospital_system/hospital_system/settings.py` — app configuration. Notable settings:
  - `INSTALLED_APPS` includes: `'accounts', 'doctors', 'patients', 'appointments', 'google_integration'`
  - Database configured as PostgreSQL in development example. Replace credentials for production.
  - `AUTH_USER_MODEL = 'accounts.User'` — project uses a custom user model.
  - Google OAuth2 placeholders: `GOOGLE_OAUTH2_CLIENT_ID` and `GOOGLE_OAUTH2_CLIENT_SECRET`
  - Email settings are configured for SMTP (placeholders present — change before using in production)

- `hosptal_management/requirements.txt` — dependency manifest for the hospital project (use this for setting up the environment)

- Templates (major locations):
  - `templates/base.html` — master layout (navbar, footer)
  - `templates/accounts/*.html` — login, signup, patient/doctor signup, profile
  - `templates/doctors/*.html` — dashboard, manage_availability, add_availability, edit_availability, appointments
  - `templates/patients/*.html` — dashboard, doctor list, doctor details
  - `templates/appointments/*.html` — booking, confirmation, my_appointments

The project contains many redesigned templates (see "UI & Templates" below for a list).

---

## Prerequisites

- Python 3.11+ (a supported Python 3.x version compatible with Django 5.x)
- PostgreSQL server (if you want to match the provided `settings.py` DB configuration)
- Node/npm is not required for this project (CSS/JS included via CDN and template files). If you later extract CSS/JS assets, you may add a front-end pipeline.

---

## Setup (development)

Below are the recommended steps to get the Hospital Management app running locally. Execute commands from the `hosptal_management/hospital_system/` folder (where `manage.py` exists).

1) Create and activate a virtual environment (zsh example):

```bash
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies (use the project requirements file):

```bash
pip install -r ../requirements.txt
```

3) Configure environment variables / secret settings:

- Open `hosptal_management/hospital_system/hospital_system/settings.py` and update or set the following for production or for local development if you prefer environment variables:
  - `SECRET_KEY` (use environment variable or `python-decouple` / `.env` file)
  - Database credentials (or switch to SQLite for quick run by altering DATABASES)
  - Email credentials (if email functionality is required)
  - Google OAuth2 settings for calendar integration

Example `.env` variables you might set (if using python-decouple):

```
SECRET_KEY=changeme
DEBUG=True
DATABASE_URL=postgres://hospital_user:password@localhost:5432/hospital_db
GOOGLE_OAUTH2_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your-secret
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=app-or-password
```

4) Prepare the database (PostgreSQL example):

- Create the database and user in PostgreSQL matching `settings.py` or update `settings.py` to point to an existing DB. Example using psql:

```bash
# create database and user (example)
psql -U postgres
CREATE DATABASE hospital_db;
CREATE USER hospital_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE hospital_db TO hospital_user;
```

5) Run migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

6) (Optional) Collect static files for production:

```bash
python manage.py collectstatic
```

7) Run the development server:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

---

## Quick run using SQLite (alternative for quick testing)

If you want a quicker option without PostgreSQL, you can temporarily switch to SQLite by editing `settings.py` and using:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Then run `migrate` and `runserver` as above.

---

## UI & Templates (what was changed)

During the UI enhancement pass, the front-end templates were redesigned for a modern, professional look. No back-end logic was changed — only HTML, CSS, and client-side JavaScript were added. The following is a non-exhaustive list of templates improved and their purpose:

- `templates/base.html` — Master layout with sticky navbar, modern footer, and global CSS/JS includes.
- `templates/home.html` (or `hospital_system/templates/home.html`) — Landing page with hero, CTA, stats, and feature cards.
- `templates/accounts/login.html` — Split layout with background imagery and styled login form.
- `templates/accounts/signup.html` — Role selection UI for Doctor vs Patient.
- `templates/accounts/patient_signup.html` — Patient registration with red/pink gradient style.
- `templates/accounts/doctor_signup.html` — Doctor registration with green gradient style.
- `templates/accounts/profile.html` — Profile view with card-based layout.
- `templates/doctors/dashboard.html` — Doctor stats, upcoming appointments, and action buttons.
- `templates/patients/dashboard.html` — Patient dashboard with appointments and CTAs.
- `templates/patients/doctors_list.html` — Doctor discovery grid with search card.
- `templates/patients/doctor_details.html` — Doctor profile and slots with booking UI.
- `templates/appointments/book_appointment.html` — Booking confirmation form with doctor preview.
- `templates/appointments/appointment_confirmation.html` — Animated success page with details.
- `templates/doctors/manage_availability.html` — Availability list with edit/delete actions.
- `templates/doctors/add_availability.html` — Add availability form (client-side validation for times).
- `templates/doctors/edit_availability.html` — Edit availability form (now styled and validated).
- `templates/doctors/appointments.html` — Doctor view for managing appointments.
- `templates/appointments/my_appointments.html` — Patient's appointments list view.

Styling notes:
- Gradients used for role differentiation (green for doctor pages, pink/red for patient pages, blue for general actions).
- Images loaded via Unsplash CDN links (no local large assets added) — ensure internet access in runtime environment.
- Client-side JavaScript added for form validation (start/end time validation), small interactive elements, and entrance animations.

---

## Testing

Run Django tests for individual apps or all at once:

```bash
# from the directory with manage.py
python manage.py test
```

If you have test modules grouped under specific apps:

```bash
python manage.py test doctors
python manage.py test appointments
```

---

## Deployment notes

For production deployment, consider the following:

- Set `DEBUG = False` and configure `ALLOWED_HOSTS`.
- Replace `SECRET_KEY` with an environment-provided secret; never commit it.
- Use PostgreSQL (or other production RDBMS) with proper credentials.
- Use Gunicorn + Nginx (or similar WSGI / reverse proxy) and secure TLS termination.
- Serve static files from a CDN or S3 behind the web server; use `python manage.py collectstatic`.
- Configure environment variables for Google OAuth and SMTP email credentials.
- If using the Google integration app, set up OAuth2 credentials in Google Cloud Console and update the client ID/secret in env.

Example production stack summary:
- Gunicorn as WSGI server
- Nginx to serve static files and reverse-proxy to Gunicorn
- PostgreSQL as database
- Redis for caching/background jobs (optional)

---

## Common troubleshooting

- Database connection errors: verify PostgreSQL server is running and credentials in `settings.py` are correct.
- Missing static files / CSS: ensure `STATIC_URL` and `STATIC_ROOT` are configured and `collectstatic` has been run.
- Email not sending: verify SMTP credentials and provider requirements (app passwords for Gmail).
- Google OAuth: ensure redirect URIs are set in Google Cloud Console and credentials match the app's config.
- Templates not reflecting UI changes: clear browser cache or confirm templates are loaded from `templates/` folder defined in `settings.py`.

---

## Contribution and development workflow

If you'd like to contribute or iterate on the project locally:

1. Fork or clone the repository.
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes, and keep UI changes in templates/CSS/JS while preserving Django template variables.
4. Run tests: `python manage.py test`.
5. Commit changes and open a Pull Request with a clear description of the change.








## Final notes & next steps

- This single-file doc is intended for GitHub upload as the primary project documentation. If you want, I can additionally:
  - Convert this into `README.md` replacing the current README
  - Generate a short `CONTRIBUTING.md` and `LICENSE`
  - Run the dev server and a quick test run to validate templates visually

