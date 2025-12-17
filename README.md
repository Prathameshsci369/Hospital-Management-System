



# 🏥 Mini Hospital Management System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg?style=flat-square)
![Django](https://img.shields.io/badge/Django-5.2.8-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue.svg)
![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg)

A comprehensive, role-based hospital management system built with Django. This system allows doctors to manage their availability and enables patients to book appointments online, with seamless Google Calendar integration and automated email notifications.

## ✨ Key Features

*   🔐 **Role-Based Access Control**: Secure and distinct dashboards for Doctors and Patients.
*   📅 **Doctor Availability Management**: Doctors can easily add, edit, and delete their time slots with an intuitive interface.
*   🗓️ **Smart Appointment Booking**: Patients can browse doctors, view available slots, and book appointments in just a few clicks.
*   🤝 **Race Condition Handling**: Robust database transactions prevent double-booking of the same slot.
*   📧 **Google Calendar Integration**: Automatically adds new appointments to both the doctor's and patient's Google Calendars upon booking.
*   ✉️ **Automated Email Notifications**: Sends welcome emails upon registration and booking confirmation emails to patients.
*   🩺 **Responsive Design**: A clean, mobile-friendly interface built with Bootstrap 5.

## 🛠️ Technology Stack

*   **Backend**: Django 5.2.8, Python 3.13
*   **Database**: PostgreSQL 13
*   **Frontend**: HTML5, CSS3, Bootstrap 5.3.0, JavaScript
*   **APIs**: Google Calendar API, Gmail SMTP Service

## 📸 Project Structure

```
hospital_management/
├── hospital_system/          # Django project settings and URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                 # User authentication and profiles
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── decorators.py
│   └── templates/
│       └── accounts/
│           ├── base.html
│           ├── login.html
│           └── ...
├── doctors/                  # Doctor-specific functionality
│   ├── models.py
│   ├── views.py
│   └── templates/
│       └── doctors/
│           ├── dashboard.html
│           └── ...
├── patients/                 # Patient-specific functionality
│   ├── models.py
│   ├── views.py
│   └── templates/
│       └── patients/
│           ├── dashboard.html
│           └── ...
├── appointments/             # Core appointment booking logic
│   ├── models.py
│   ├── views.py
│   └── templates/
│       └── appointments/
│           ├── book_appointment.html
│           └── ...
├── google_integration/       # Google Calendar API logic
│   ├── models.py
│   ├── views.py
│   └── ...
├── templates/               # Global templates
│   └── base.html
├── manage.py
├── requirements.txt
└── .env                  # Environment variables (DB credentials, email settings)
```

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.8+
*   PostgreSQL
*   pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hospital-management-system.git
cd hospital-management-system
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root and add your configuration:

```ini
# .env

# Database Settings
DB_NAME=hospital_db
DB_USER=hospital_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Email Settings (for Gmail, use an App Password)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL='Hospital Management <your-email@gmail.com>'
```

### 5. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will now be available at `http://127.0.0.1:8000/`.

## 🔐 API Integrations

### Google Calendar Integration

This feature uses the OAuth 2.0 flow to get permission from users to manage their Google Calendars.

1.  **Setup**: Create a project in the [Google Cloud Console](https://console.cloud.google.com/), enable the Google Calendar API, and create OAuth 2.0 credentials.
2.  **Connect**: Users can connect their accounts via a "Connect to Google Calendar" button on their profile page.
3.  **Automate**: Upon successful appointment booking, the system automatically creates an event in both the doctor's and patient's calendars.

### Email Service

The system uses Django's built-in email backend to send notifications.

*   **Welcome Emails**: Sent to new users upon registration.
*   **Booking Confirmations**: Sent to patients after they successfully book an appointment.

## 📸 Usage

### For Doctors

1.  **Sign Up**: Create a new doctor account.
2.  **Log In**: Access the dashboard.
3.  **Set Availability**: Add the time slots you are available for appointments.
4.  **View Appointments**: See a list of all your scheduled appointments.

### For Patients

1.  **Sign Up**: Create a new patient account.
2.  **Log In**: Access the dashboard.
3.  **Find Doctors**: Browse the list of available doctors and their specializations.
4.  **Book Appointment**: Select a doctor, view their available slots, and book an appointment.

## 🤝 Contributing

Contributions are what make the open-source community amazing. Any help you can provide would be greatly appreciated!

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a [Pull Request](https://github.com/your-username/hospital-management-system/pulls).

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

*   Django Team - For the excellent web framework.
*   Bootstrap Team - For the responsive UI components.
*   Google - For the powerful Calendar API.

---

**Built with ❤️ for a more efficient healthcare experience.**
```

### How to Use This File

1.  Save the content above as `README.md` in the root directory of your project.
2.  Commit it to your Git repository:
    ```bash
    git add README.md
    git commit -m "Add comprehensive, modern README"
    git push
    ```

This README provides a clear, professional, and modern introduction to your project, making it easy for others to understand and contribute.
