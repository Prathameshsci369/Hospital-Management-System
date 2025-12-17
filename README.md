
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
