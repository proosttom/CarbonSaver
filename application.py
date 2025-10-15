"""
CarbonSaver Application Entry Point for AWS Elastic Beanstalk

Elastic Beanstalk looks for 'application.py' or 'app.py' with an 'application' variable.
This file imports the Flask app and exposes it as 'application'.
"""

from app import app as application

if __name__ == "__main__":
    application.run()
