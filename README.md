



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
