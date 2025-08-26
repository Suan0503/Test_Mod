#!/usr/bin/env python
"""
Flask-Migrate management script
Run migrations with: python manage.py db upgrade
"""
import os
from flask.cli import FlaskGroup
from app import app

cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
