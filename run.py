from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    Config.init_app()  # Show debug info
    app.run(debug=Config.DEBUG, port=Config.PORT)
