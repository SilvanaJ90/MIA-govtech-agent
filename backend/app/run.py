#!/usr/bin/env python3
"""
Entry point for the Flask application.

This script initializes and runs the Flask app using the application
factory pattern defined in the `create_app` function inside the `app` package.

Running this script directly will start the Flask development server.
"""

from app import create_app

# Create the Flask application instance using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the Flask app in debug mode for development purposes
    app.run(debug=True)
