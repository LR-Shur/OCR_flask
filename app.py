#必备的东西
from flask import Flask
from flaskr import config
from flaskr.exts import db

#后台路由
from flaskr.blueprints.base import bp as base_bp
from flaskr.blueprints.interface import bp as interface_bp
#数据库
from flask_migrate import  Migrate


#初始化
app=Flask(__name__,template_folder="flaskr/templates",static_folder="flaskr/static")

app.config.from_object(config)

db.init_app(app)

migrate = Migrate(app,db)

#导入路由
app.register_blueprint(base_bp)
app.register_blueprint(interface_bp)

#定义密钥
app.secret_key = "this_is_key"

if __name__ == '__main__':
    app.run(host="192.168.156.66")