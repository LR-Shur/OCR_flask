from flask import Blueprint, render_template,redirect,url_for,request,session,flash
from flaskr.models import Administrator,Card_id,User

bp = Blueprint('base', __name__,url_prefix='/')


#主菜单
@bp.route("/")
def base():
    if 'logged_in' in session and session["logged_in"]==True:  # 检查登录状态
        return redirect(url_for('base.dashboard'))  # 已登录，跳转到仪表盘
    return redirect(url_for('base.login'))  # 未登录，跳转到登录页


# 管理登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 从数据库中查找管理
        admin = Administrator.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_id'] = admin.id  # 登录成功，设置用户会话
            session['logged_in'] = True
            flash('登录成功！', 'success')
            return redirect(url_for('base.dashboard'))  # 跳转到仪表盘
        else:
            flash('用户名或密码错误，请重试。', 'danger')

    return render_template("login.html")  # 如果是 GET 请求，返回登录页面

# 仪表盘


@bp.route('/dashboard')
def dashboard():
    # 手动检查用户是否登录
    if 'logged_in' not in session:
        flash('请先登录。', 'warning')
        return redirect(url_for('base.login'))  # 重定向到登录页面

    user_count = 100  # 示例数据
    card_count = 200  # 示例数据
    return render_template('dashboard.html', user_count=user_count, card_count=card_count)




# 卡片管理页面
@bp.route('/cards')
def card_list():
    page = request.args.get('page', 1, type=int)  # 获取当前页码，默认为1
    per_page = 10  # 每页显示的条数

    # 使用 paginate 方法查询卡片数据，注意模型名和数据库的连接
    pagination = Card_id.query.paginate(page=page, per_page=per_page, error_out=False)

    cards = pagination.items  # 获取当前页的卡片数据
    return render_template('cards.html', cards=cards, pagination=pagination)

#用户管理
@bp.route('/user')
def user_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)

    users = pagination.items
    return render_template('user.html', users=users, pagination=pagination)