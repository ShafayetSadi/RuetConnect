# Gemini Code Assistant Context

This document provides context for the Gemini code assistant to understand the RUET CampusConnect project.

## Project Overview

**RUET CampusConnect** is a centralized communication and collaboration platform tailored for the vibrant community of Rajshahi University of Engineering & Technology (RUET). It aims to provide a focused, clutter-free, and productive environment for communication within and across student groups, faculty, and staff. The project is built with Python and Django, featuring a modern frontend powered by HTMX and Tailwind CSS.

## Key Technologies & Architecture

- **Backend:** Python 3.12+, Django 5.0+
- **Frontend:** HTMX for dynamic interactions, Tailwind CSS for styling, Alpine.js for lightweight JavaScript
- **Database:** SQLite (development), PostgreSQL ready (production)
- **Authentication:** `django-allauth` with custom user model
- **Package Management:** `uv` for fast Python package management
- **Code Quality:** Pre-commit hooks, flake8, black, isort
- **CI/CD:** GitHub Actions for testing, linting, and security analysis

## Project Structure

```text
ruetconnect/
├── apps/                    # Django applications
│   ├── accounts/           # User authentication, profiles, custom user model
│   ├── campus/             # Homepage, organizations, campus-wide features
│   ├── posts/              # Forum posts, content management
│   ├── comments/           # Nested comment system with replies
│   ├── threads/            # Discussion categories and topics
│   └── votes/              # Upvote/downvote system, saved posts
├── config/                  # Project configuration
│   ├── settings/           # Environment-specific settings
│   │   ├── base.py         # Base settings with allauth config
│   │   ├── dev.py          # Development settings
│   │   └── prod.py         # Production settings
│   └── urls.py             # Main URL routing
├── shared/                  # Shared utilities and models
│   └── models.py           # BaseModel with UUID, timestamps, soft delete
├── templates/               # HTML templates
│   ├── account/            # Allauth authentication templates
│   ├── campus/             # Campus pages templates
│   ├── posts/              # Post-related templates
│   ├── comments/           # Comment templates
│   ├── threads/            # Thread templates
│   └── partials/           # Reusable template components
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User-uploaded content
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Locked dependency versions
└── manage.py               # Django management script
```

## Core Features & Functionality

### 🔐 Authentication System

- **Custom User Model:** Extended Django User with RUET-specific fields
- **User Types:** Student, Faculty, Staff, Alumni
- **Departments:** All RUET academic departments (CSE, EEE, ME, CE, etc.)
- **Profile Management:** Avatar, bio, social links, privacy settings
- **Allauth Integration:** Social login, email verification, password management

### 🏛️ Campus Organization System

- **Organizations:** Clubs, societies, associations, committees
- **Membership Management:** Roles (Member, Moderator, Admin, President, etc.)
- **Status Tracking:** Pending, Active, Inactive, Banned members

### 🧵 Content Management

- **Threads:** Topic-based discussion categories
- **Posts:** Rich content with text, images, videos, links, polls, events
- **Comments:** Nested comment system with infinite replies
- **Media Support:** File uploads, external links, thumbnails

### 👍 Engagement Features

- **Voting System:** Upvote/downvote posts and comments
- **Saved Posts:** User bookmarking system
- **Reputation System:** User scoring based on activity
- **Search:** Full-text search across campus content

### 🎨 User Experience

- **Responsive Design:** Mobile-first approach with Tailwind CSS
- **Dark/Light Theme:** User-selectable themes with Alpine.js
- **HTMX Integration:** Dynamic interactions without page reloads
- **Accessibility:** Semantic HTML, proper ARIA labels

## Key Models & Relationships

### User & Profile

```python
# Custom User Model
- id (BigAutoField)
- username, email, password
- first_name, last_name
- student_id (unique, 7 chars)
- user_type (student/faculty/staff/alumni)
- department (academic department)
- series (admission year)
- is_verified (RUET verification status)

# Profile Model (OneToOne with User)
- avatar, bio, birth_date
- phone, address
- social_links (JSON)
- interests, skills (JSON arrays)
- reputation_score
- privacy settings
```

### Content Models

```python
# Organization
- name, slug, description
- org_type, logo, cover_image
- member_count, is_active

# Thread
- title, slug, description
- thread_type, organization (FK)
- created_by, is_pinned, is_locked

# Post
- title, slug, content
- post_type, thread (FK), author (FK)
- engagement metrics, status fields

# Comment
- content, post (FK), author (FK)
- parent (self-referencing for replies)
- level, path (materialized path)
- upvotes, downvotes
```

## Authentication & Security

### Allauth Configuration

- **Login Methods:** Username or email
- **Email Verification:** Disabled for development
- **Signup Fields:** RUET-specific information collection
- **Rate Limiting:** 5 failed login attempts per minute
- **Custom Forms:** Extended signup with validation

### Security Features

- **CSRF Protection:** Enabled on all forms
- **Session Management:** Secure session handling
- **User Verification:** RUET member verification system
- **Content Moderation:** Report, block, and removal tools

## Development Workflow

### Setup Commands

```bash
# Install dependencies
uv sync

# Database operations
uv run python manage.py migrate
uv run python manage.py makemigrations

# Development server
uv run python manage.py runserver

# Tailwind CSS watching
uv run python manage.py tailwind watch

# Code quality
uv run pre-commit run --all-files
```

### Environment Configuration

```bash
# Required environment variables
DJANGO_SETTINGS_MODULE=config.settings.dev
SECRET_KEY=<your-secret-key>
```

## Code Quality & Standards

### Pre-commit Hooks

- **Black:** Code formatting
- **isort:** Import sorting
- **flake8:** Linting with custom rules
- **YAML validation:** Configuration file checks

### Testing Strategy

- **Unit Tests:** Model and view testing
- **Integration Tests:** URL routing and form submission
- **CI/CD:** Automated testing on push/PR

### Code Style

- **Line Length:** 119 characters max
- **Indentation:** 4 spaces
- **Quotes:** Double quotes for strings
- **Import Order:** Standard library, third-party, local

## Deployment & Production

### Environment Separation

- **Development:** SQLite, debug enabled, console email backend
- **Production:** PostgreSQL, debug disabled, proper email backend
- **Settings Inheritance:** Base settings with environment-specific overrides

### Static Files

- **Tailwind CSS:** Compiled from source with DaisyUI components
- **HTMX:** Latest version for dynamic interactions
- **Alpine.js:** Lightweight JavaScript framework

## Contributing Guidelines

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install dependencies with `uv sync`
4. Make changes following the code style
5. Run pre-commit hooks
6. Submit a pull request

### Code Review Process

- All changes require pull request review
- Automated testing must pass
- Code style compliance enforced
- Security review for authentication changes

## Troubleshooting Common Issues

### Authentication Problems

- Check `django-allauth` configuration in settings
- Verify custom user model settings
- Ensure proper URL routing for auth views

### Template Issues

- Check template inheritance in `base.html`
- Verify template directory structure
- Ensure proper context data in views

### Database Issues

- Run migrations: `python manage.py migrate`
- Check model relationships and foreign keys
- Verify custom model manager methods

## Performance Considerations

### Database Optimization

- Use `select_related` and `prefetch_related` for related queries
- Implement proper database indexing
- Consider caching for frequently accessed data

### Frontend Performance

- HTMX for minimal JavaScript overhead
- Tailwind CSS for optimized CSS delivery
- Lazy loading for images and media

## Security Best Practices

### User Input Validation

- Form validation with Django forms
- Model field validation
- XSS protection with template escaping

### Authentication Security

- Secure password hashing
- Session security
- CSRF protection on all forms

This context should provide comprehensive understanding of the RUET CampusConnect project for effective code assistance and development guidance.
