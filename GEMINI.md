# Gemini Code Assistant Context

This document provides context for the Gemini code assistant to understand the RUET CampusConnect project.

## Project Overview

**RUET CampusConnect** is a centralized communication and collaboration platform tailored for the vibrant community of Rajshahi University of Engineering & Technology (RUET). It aims to provide a focused, clutter-free, and productive environment for communication within and across student groups, faculty, and staff. The project is built with Python and Django, featuring a modern frontend powered by HTMX and Tailwind CSS.

## Key Technologies

- **Backend:** Python, Django
- **Frontend:** HTMX, Tailwind CSS, Alpine.js
- **Database:** SQLite (for development)
- **Authentication:** `django-allauth`
- **Dependencies:** Managed with `pip` and defined in `requirements.txt` and `pyproject.toml`.

## Building and Running the Project

To get the project up and running, follow these steps:

1.  **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Create a `.env` file:**

    Create a `.env` file in the project root and add the following environment variables:

    ```
    DJANGO_SETTINGS_MODULE=config.settings.dev
    SECRET_KEY=<your-secret-key>
    ```

    You can generate a secret key using Django's `get_random_secret_key()` function.

3.  **Run database migrations:**

    ```bash
    python manage.py migrate
    ```

4.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

5.  **Run the Tailwind CSS CLI:**

    In a seperate shell, run the following command to start the Tailwind CLI watcher:

    ```bash
    python manage.py tailwind watch
    ```

## Development Conventions

- The project follows a modular structure, with different functionalities separated into Django apps within the `apps` directory.
- The settings are split into `base.py`, `dev.py`, and `prod.py` for different environments.
- The project uses `django-htmx` to enhance the user experience with dynamic interactions without writing a lot of JavaScript.
- Styling is done using Tailwind CSS, a utility-first CSS framework.
- The project uses `pre-commit` hooks to enforce code quality. You can set it up by running:
  ```bash
  pre-commit install
  ```
