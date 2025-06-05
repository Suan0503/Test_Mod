from flask import Flask
from extensions import db
from routes.message import message_bp

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)  # 或用 os.environ/Getenv 等
db.init_app(app)

app.register_blueprint(message_bp)

if __name__ == "__main__":
    app.run()
