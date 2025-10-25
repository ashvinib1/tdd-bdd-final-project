"""
Package: service

This module creates and configures the Flask app,
sets up SQLAlchemy, logging, and imports routes and models.
"""

import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from service import config
from service.common import log_handlers

# Create Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(config)

# Create SQLAlchemy db instance
db = SQLAlchemy(app)

# Set up logging
log_handlers.init_logging(app, "gunicorn.error")
app.logger.info(70 * "*")
app.logger.info("  P E T SERVICE RUNNING  ".center(70, "*"))
app.logger.info(70 * "*")

# Import models and routes AFTER app & db creation to avoid circular imports
from service import models, routes
from service.common import error_handlers, cli_commands

# Initialize database tables
try:
    models.init_db(app)
except Exception as error:
    app.logger.critical("%s: Cannot continue", error)
    sys.exit(4)

app.logger.info("Service initialized!")
