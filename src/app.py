"""
Main Flask application entry point.

Author(s): Purple T-Pythons Team
"""

from src.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
