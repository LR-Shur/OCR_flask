
from flaskr.exts import db


class Administrator(db.Model):
    __tablename__ = 'administrators'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def check_password(self, password):
        return self.password == password


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' 或 'admin'
    # 通过 cards 属性与 Card_id 建立关系



class Card_id(db.Model):
    __tablename__ = 'card_id'


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_path = db.Column(db.String(255), nullable=False)  # 图片的存储路径
    name = db.Column(db.String(800), nullable=True)  # 名称
    gender = db.Column(db.String(100), nullable=True)  # 性别
    nation = db.Column(db.String(200), nullable=True)  # 民族
    birthday = db.Column(db.String(200), nullable=True)  # 出生日期
    address = db.Column(db.String(255), nullable=True)  # 住址
    id_number = db.Column(db.String(200), nullable=True)  # 身份证号

    # 设置与用户的外键关联
    # 外键字段，指向 User 表的 id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 绑定到 User 表

    # 反向关系定义，虽然不必要，但可以保留以方便查询
    user = db.relationship('User', backref='cards', lazy=True)
