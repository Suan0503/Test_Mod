# Flask Application Migration Guide

This document provides instructions for migrating and running the reorganized Flask application.

## Project Structure

The Flask application has been reorganized into a clean, maintainable structure:

```
Test_Mod/
├── app.py                  # Main Flask application with factory pattern
├── config.py              # Configuration management
├── extensions.py          # Flask extensions (SQLAlchemy, Migrate, LINE Bot)
├── manage.py              # Migration management script
├── requirements.txt       # Python dependencies
├── Procfile               # Deployment configuration
├── models/                # Database models
│   ├── whitelist.py
│   └── blacklist.py
├── routes/                # Blueprint routes
│   ├── list_admin.py      # Admin list management
│   └── message.py         # LINE Bot message handling
├── templates/admin/       # Admin templates
│   ├── base.html
│   ├── index.html
│   ├── whitelist_form.html
│   └── blacklist_form.html
├── hander/                # LINE Bot handlers
├── utils/                 # Utility functions
├── migrations/            # Database migrations
└── smoke_test.py          # Smoke test script
```

## Environment Variables

Set the following environment variables:

### Required for Production
- `SECRET_KEY`: Flask secret key for session security
- `DATABASE_URL`: Database connection URL (defaults to `sqlite:///data.db`)
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Bot channel access token
- `LINE_CHANNEL_SECRET`: LINE Bot channel secret

### Optional
- `FLASK_CONFIG`: Configuration name (`development`, `production`, `testing`)
- `FLASK_DEBUG`: Enable debug mode (`0` or `1`)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `PORT`: Application port (default: `5000`)

## Migration Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file or set environment variables:

```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="your-database-url"
export LINE_CHANNEL_ACCESS_TOKEN="your-line-token"
export LINE_CHANNEL_SECRET="your-line-secret"
```

### 3. Initialize Database Migrations

If this is a fresh installation:

```bash
python manage.py db init
python manage.py db migrate -m "Initial migration"
python manage.py db upgrade
```

If migrating from existing database:

```bash
python manage.py db upgrade
```

### 4. Run Smoke Tests

Verify the application is working:

```bash
python smoke_test.py
```

### 5. Start the Application

For development:

```bash
python app.py
```

For production (with gunicorn):

```bash
gunicorn app:app
```

## Functionality Verification Checklist

After migration, verify the following functionality:

### Core Application
- [ ] Application starts without errors
- [ ] Database connection works
- [ ] Home page loads (`/`)

### Admin List Management (`/admin/list/`)
- [ ] List view displays whitelist and blacklist items
- [ ] Search functionality works
- [ ] Create new whitelist item
- [ ] Edit existing whitelist item
- [ ] Delete whitelist item
- [ ] Create new blacklist item
- [ ] Edit existing blacklist item
- [ ] Delete blacklist item
- [ ] Transfer from whitelist to blacklist

### LINE Bot Integration
- [ ] LINE webhook endpoint responds (`/callback`)
- [ ] Follow events work
- [ ] Message handling works
- [ ] Verification flows work
- [ ] Admin commands work

### Error Handling
- [ ] Database errors are caught and rolled back
- [ ] User-friendly error messages are displayed
- [ ] Logs are written for debugging

## New Features Added

### 1. Flask-Migrate Support
- Database schema versioning
- Safe database migrations
- Rollback capability

### 2. Improved Error Handling
- Try/catch blocks around database operations
- Automatic rollback on errors
- Proper logging for debugging

### 3. Configuration Management
- Environment-based configuration
- Separate configs for development/production/testing
- Better default values

### 4. Enhanced Templates
- Bootstrap 5 styling
- Flash message support with dismissible alerts
- Base template to reduce duplication
- Responsive design

### 5. Application Factory Pattern
- Better testability
- Multiple app instances support
- Cleaner separation of concerns

## Troubleshooting

### Database Issues
- Ensure DATABASE_URL is set correctly
- Run migrations: `python manage.py db upgrade`
- Check database permissions

### LINE Bot Issues
- Verify LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET
- Check LINE webhook URL configuration
- Verify SSL certificate for webhook endpoint

### Import Errors
- Ensure all dependencies are installed
- Check Python path configuration
- Verify file structure matches expected layout

## Deployment Notes

### Railway/Heroku
- Set environment variables in platform dashboard
- Ensure Procfile is present
- Run migrations as part of deployment process

### Docker
- Use provided Dockerfile
- Set environment variables in container
- Mount persistent volume for SQLite (if used)

### Traditional Server
- Use gunicorn or uwsgi
- Set up reverse proxy (nginx/apache)
- Configure SSL certificates
- Set up log rotation

## Security Considerations

- Change default SECRET_KEY
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regularly update dependencies
- Monitor application logs