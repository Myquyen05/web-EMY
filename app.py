from flask import Flask
from flask_login import LoginManager
from models import db, User, Service
from werkzeug.security import generate_password_hash
from routes import public_bp, admin_bp, SERVICES_SEED
from auth import auth_bp
import os

app = Flask(__name__)

# ── CẤU HÌNH ──────────────────────────────────────────────
app.config['SECRET_KEY']                  = 'emy-secret-key-2026'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH']          = 50 * 1024 * 1024  # 50MB upload

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'center.db')

# ── KHỞI TẠO ──────────────────────────────────────────────
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view          = 'auth.login'
login_manager.login_message       = 'Vui lòng đăng nhập để tiếp tục.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── BLUEPRINTS ─────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)

# ── KHỞI TẠO DB & DỮ LIỆU MẪU ────────────────────────────
def init_db():
    os.makedirs('database', exist_ok=True)
    os.makedirs('static/uploads/posts', exist_ok=True)
    os.makedirs('static/uploads/services', exist_ok=True)
    db.create_all()

    # Tạo admin mặc định
    if not User.query.filter_by(email='admin@emycenter.vn').first():
        db.session.add(User(
            fullname='Quản trị viên',
            email='admin@emycenter.vn',
            password_hash=generate_password_hash('Admin@123'),
            role='admin'
        ))

    # Tạo giáo viên mẫu
    if not User.query.filter_by(email='giaovien@emycenter.vn').first():
        db.session.add(User(
            fullname='Nguyễn Thị Lan',
            email='giaovien@emycenter.vn',
            password_hash=generate_password_hash('Teacher@123'),
            role='teacher'
        ))

    # Seed 6 dịch vụ
    for svc_data in SERVICES_SEED:
        if not Service.query.filter_by(slug=svc_data['slug']).first():
            svc = Service(
                slug       = svc_data['slug'],
                name       = svc_data['name'],
                icon       = svc_data['icon'],
                color      = svc_data['color'],
                short_desc = svc_data['short_desc'],
                intro      = svc_data['intro'],
                content    = svc_data['content'],
                benefits   = svc_data['benefits'],
                target_age = svc_data['target_age'],
                duration   = svc_data['duration'],
                video_url  = svc_data.get('video_url',''),
                order      = svc_data['order'],
                is_active  = True,
            )
            db.session.add(svc)

    db.session.commit()
    print('✅ Database và dịch vụ đã sẵn sàng!')
    print('👤 Admin:    admin@emycenter.vn    / Admin@123')
    print('👩‍🏫 GV:       giaovien@emycenter.vn / Teacher@123')
    print('🌐 Chạy tại: http://127.0.0.1:5000')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
