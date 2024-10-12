import base64
import os
from flask import Blueprint, request, redirect, url_for, flash,jsonify,session,send_file
from werkzeug.utils import secure_filename
from flaskr.exts import db
from flaskr.models import Card_id
from flaskr.models import User
from flaskr.tools.data_json import create_response
from ocr.detect_interface import detect_interface
import cv2

bp = Blueprint('interface', __name__, url_prefix='/interface')

# 设置允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# /interface/upload这个要传一个图片给我，然后我传json给你，"image_path": file_path,
#             "name": ocr_result["姓名"],
#             "gender": ocr_result["性别"],
#             "nation": ocr_result["民族"],
#             "birthday": ocr_result["出生"],
#             "address": ocr_result["住址"],
#             "id_number": ocr_result["公民身份号码"]
@bp.route('/upload', methods=['POST'])
def upload_image():


    # 检查是否有文件上传
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # 如果文件名合法，保存文件
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)  # 保存到uploads文件夹
        file.save(file_path)

        img = cv2.imread(file_path)

        # 调用OCR函数识别
        ocr_result = detect_interface(img)
        print(ocr_result)

        # 将结果保存到数据库
        username = session.get('username_id')
        if username is None:
            username = 1  # 默认用户ID为1
        card = Card_id(image_path=file_path, name=ocr_result["姓名"],gender=ocr_result["性别"],nation=ocr_result["民族"],
                       birthday=ocr_result["出生"],address=ocr_result["住址"],id_number=ocr_result["公民身份号码"], user_id=username)  # 绑定上传者
        # db.session.add(card)
        # db.session.commit()

        flash('Image uploaded and OCR performed successfully!')

        response = {
            "image_path": file_path,
            "name": ocr_result["姓名"],
            "gender": ocr_result["性别"],
            "nation": ocr_result["民族"],
            "birthday": ocr_result["出生"],
            "address": ocr_result["住址"],
            "id_number": ocr_result["公民身份号码"]
        }
        return create_response(200, '上传成功', response)

    else:
        response = {
        }
        flash('Invalid file format')
        return create_response(400, '上传失败', response)

#你把前端用户修改好的信息传给我，我把信息存到数据库里，用json传给我，也就是说你要写一个页面用于用户修改
@bp.route('/save_image', methods=['POST'])
def save_image():
    # 获取图片数据
    image_path = request.json.get('image_path')

    name = request.json.get('name')
    gender = request.json.get('gender')
    nation = request.json.get('nation')
    birthday = request.json.get('birthday')
    address = request.json.get('address')
    id_number = request.json.get('id_number')
    username = session.get('username_id')
    if username is None:
        username = 1  # 默认用户ID为1
    card = Card_id(image_path=image_path, name=name,gender=gender,nation=nation,
                   birthday=birthday,address=address,id_number=id_number, user_id=username)
    db.session.add(card)
    db.session.commit()
    response = {}
    return create_response(200, 'oj8k了', response)

#注册路由，传入用户名，邮箱，密码，返回注册成功，邮箱你乱改一个就行
@bp.route('/register', methods=['POST'])
def register_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    if(email is None):
        email="1234567890@qq.com"

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return create_response(400, '用户名已存在')



    # 检查邮箱是否已存在
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return create_response(400, '邮箱已存在')

    # 创建新用户
    new_user = User(
        username=username,
        email=email,
        password=password,
        role = 'user'
    )
    db.session.add(new_user)
    db.session.commit()

    flash('注册成功！', 'success')
    return create_response(200, '注册成功')

#登录路由，传入用户名和密码，返回登录成功
@bp.route('/login', methods=['POST'])
def login_user():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        session['user_id'] = user.id  # 将用户ID存入session
        return create_response(200, '登录成功', {'user_id': user.id})
    else:
        return create_response(400, '用户名或密码错误')


@bp.route('/user_info', methods=['GET'])
def get_user_info():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return create_response(200, '用户信息获取成功', {
                'username': user.username,
                'email': user.email,
                'role': user.role
            })
    return create_response(400, '未登录或用户不存在')

#获取用户上传的图片，一个大json,里面每个小json包含图片的base64编码和图片信息内容为
# 'image_path': image.image_path,
#             'image_base64': img_base64,  # Base64编码的图片数据
#             'name': image.name,
#             'gender': image.gender,
#             'nation': image.nation,
#             'birthday': image.birthday,
#             'address': image.address,
#             'id_number': image.id_number,
#             'upload_time': image.created_at  # 假设有这个字段
@bp.route('/user_images', methods=['GET'])
def get_user_images():
    # 获取当前登录用户的ID
    user_id = session.get('user_id')

    # 如果用户未登录
    if not user_id:
        return create_response(400, '用户未登录')

    # 查询该用户上传的所有图片
    user_images = Card_id.query.filter_by(user_id=user_id).all()

    # 如果用户没有上传图片
    if not user_images:
        return create_response(404, '用户没有上传任何图片')

    # 将查询结果转换为列表形式，包含Base64编码的图片数据
    images_data = []
    for image in user_images:
        image_path = image.image_path

        # 将图片文件读取为二进制数据
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()

        # 将图片数据转换为Base64编码
        img_base64 = base64.b64encode(img_data).decode('utf-8')

        # 构建图片信息字典，包含图片Base64内容
        images_data.append({
            'image_path': image.image_path,
            'image_base64': img_base64,  # Base64编码的图片数据
            'name': image.name,
            'gender': image.gender,
            'nation': image.nation,
            'birthday': image.birthday,
            'address': image.address,
            'id_number': image.id_number,

        })

    # 返回用户图片信息及Base64编码的图片内容
    return create_response(200, '用户图片获取成功', images_data)


@bp.route('/download_image/<image_path>', methods=['GET'])
def download_image(image_path):
    # 获取完整的图片路径
    image_full_path = os.path.join(r'M:\python\OCR_flask\uploads', image_path)

    # 检查图片是否存在
    if not os.path.exists(image_full_path):
        return create_response(404, '图片未找到')

    # 使用 send_file 将图片文件发送给前端
    return send_file(image_full_path, mimetype='image/jpeg')