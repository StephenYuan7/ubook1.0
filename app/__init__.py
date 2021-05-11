from .app import Flask


def register_blueprints(app):
    from app.api.v2 import create_blueprint_v2
    app.register_blueprint(create_blueprint_v2(), url_prefix='/v2')


# 注册数据库orm对象
def register_plugin(app):
    from app.models.base import db
    db.init_app(app)
    with app.app_context():
        db.create_all()


# 注册websocket对象
def register_extensions(app):
    from .extension.websocket import socketio
    socketio.init_app(app)


# 注册flask的核心对象
def create_app():
    # __name__为当前文件
    app = Flask(__name__)

    # 导入两个配置文件
    app.config.from_object('app.config.setting')
    app.config.from_object('app.config.secure')

    register_blueprints(app)
    register_plugin(app)
    register_extensions(app)
    return app
