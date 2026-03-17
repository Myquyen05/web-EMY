from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from functools import wraps
from models import db, Student, Post, Event, Registration, Consultation, Progress, FAQ, User, Service
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os, uuid, json

public_bp = Blueprint('public', __name__)
admin_bp  = Blueprint('admin',  __name__, url_prefix='/admin')

ALLOWED_IMG = {'png','jpg','jpeg','gif','webp'}
ALLOWED_VID = {'mp4','webm','ogg','mov'}
ALLOWED_ALL = ALLOWED_IMG | ALLOWED_VID

def save_upload(file, subfolder='posts'):
    if not file or file.filename == '':
        return None, None
    ext = file.filename.rsplit('.',1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_ALL:
        return None, None
    fname  = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.root_path, 'static', 'uploads', subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, fname))
    return f"uploads/{subfolder}/{fname}", ('video' if ext in ALLOWED_VID else 'image')

def get_media_type(path):
    if not path: return None
    if any(x in path for x in ['youtube.com','youtu.be','vimeo.com']): return 'youtube'
    ext = path.rsplit('.',1)[-1].lower() if '.' in path else ''
    if ext in ALLOWED_VID: return 'video'
    if ext in ALLOWED_IMG: return 'image'
    return 'image_url'

def get_yt_id(url):
    if not url: return None
    if 'v=' in url:         return url.split('v=')[-1].split('&')[0]
    if 'youtu.be' in url:   return url.split('youtu.be/')[-1].split('?')[0]
    return None

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

# ── DỮ LIỆU SEED CHO 6 DỊCH VỤ ─────────────────────────
SERVICES_SEED = [
    {
        'slug': 'can-thiep-aba',
        'name': 'Can thiệp hành vi ABA',
        'icon': '🧩',
        'color': '#1558B0',
        'short_desc': 'Phân tích hành vi ứng dụng, giúp trẻ học kỹ năng mới và tăng cường giao tiếp xã hội hiệu quả.',
        'intro': 'ABA (Applied Behavior Analysis) là phương pháp can thiệp dựa trên khoa học hành vi, được nghiên cứu và công nhận rộng rãi nhất thế giới trong điều trị tự kỷ. Tại EMY, chương trình ABA được cá nhân hóa hoàn toàn cho từng trẻ.',
        'content': '''<h2>ABA là gì?</h2>
<p>Phân tích hành vi ứng dụng (Applied Behavior Analysis - ABA) là hệ thống can thiệp khoa học tập trung vào việc hiểu và cải thiện hành vi. ABA sử dụng các nguyên tắc học tập để tăng cường hành vi có lợi và giảm thiểu hành vi cản trở.</p>
<h2>Tại sao ABA hiệu quả với trẻ tự kỷ?</h2>
<p>ABA được xem là <strong>"tiêu chuẩn vàng"</strong> trong can thiệp tự kỷ bởi:</p>
<ul>
<li>Được hỗ trợ bởi hơn 50 năm nghiên cứu khoa học</li>
<li>Cá nhân hóa hoàn toàn theo từng trẻ</li>
<li>Có thể đo lường tiến trình một cách rõ ràng</li>
<li>Áp dụng được trong mọi môi trường: lớp học, gia đình, cộng đồng</li>
</ul>
<h2>Quy trình can thiệp ABA tại EMY</h2>
<p>Mỗi trẻ được tiếp cận theo quy trình chuẩn hóa quốc tế, kết hợp linh hoạt các kỹ thuật DTT, NET, PRT tùy theo nhu cầu và giai đoạn phát triển của từng bé.</p>
<h2>Kết quả kỳ vọng</h2>
<p>Sau 6–12 tháng can thiệp ABA cường độ cao, phần lớn trẻ tại EMY cải thiện rõ rệt về giao tiếp, kỹ năng xã hội, học tập và giảm thiểu hành vi không phù hợp.</p>''',
        'benefits': json.dumps(['Tăng cường kỹ năng giao tiếp và ngôn ngữ','Cải thiện kỹ năng xã hội và chơi cùng bạn','Giảm hành vi không phù hợp','Xây dựng kỹ năng tự phục vụ','Tăng khả năng tập trung và học tập','Cải thiện kỹ năng tiền học đường']),
        'target_age': '18 tháng – 12 tuổi',
        'duration': '1–3 giờ/buổi · 3–5 buổi/tuần',
        'video_url': '',
        'order': 1,
    },
    {
        'slug': 'tri-lieu-ngon-ngu',
        'name': 'Trị liệu ngôn ngữ',
        'icon': '🗣️',
        'color': '#27B394',
        'short_desc': 'Phát triển khả năng giao tiếp lời nói và phi lời nói, ngôn ngữ hiểu và biểu đạt toàn diện.',
        'intro': 'Trị liệu ngôn ngữ tại EMY giúp trẻ phát triển toàn diện khả năng giao tiếp — từ ngôn ngữ lời nói, phi lời nói, đến kỹ năng xã hội ngôn ngữ. Mỗi chương trình được thiết kế riêng theo nhu cầu từng trẻ.',
        'content': '''<h2>Trị liệu ngôn ngữ là gì?</h2>
<p>Trị liệu ngôn ngữ là dịch vụ chuyên biệt giúp trẻ phát triển và cải thiện khả năng giao tiếp, bao gồm giao tiếp lời nói, phi lời nói, khả năng hiểu ngôn ngữ và sử dụng ngôn ngữ để biểu đạt.</p>
<h2>Các lĩnh vực can thiệp</h2>
<ul>
<li><strong>Ngôn ngữ tiếp nhận:</strong> Khả năng hiểu lời nói, hướng dẫn, câu hỏi</li>
<li><strong>Ngôn ngữ biểu đạt:</strong> Sử dụng từ ngữ, câu để giao tiếp</li>
<li><strong>Giao tiếp phi lời nói:</strong> Cử chỉ, ánh mắt, nét mặt</li>
<li><strong>AAC:</strong> Hệ thống giao tiếp thay thế và hỗ trợ (PECS, thiết bị)</li>
<li><strong>Phát âm:</strong> Cải thiện độ rõ ràng của lời nói</li>
</ul>
<h2>Phương pháp tại EMY</h2>
<p>Chuyên viên ngôn ngữ trị liệu tại EMY sử dụng đa dạng phương pháp: PECS, Hanen, DIR/Floortime, Social Stories — tạo môi trường giao tiếp tự nhiên và vui vẻ.</p>''',
        'benefits': json.dumps(['Phát triển vốn từ vựng phong phú','Cải thiện khả năng nói rõ ràng','Tăng cường giao tiếp chủ động','Phát triển kỹ năng đàm thoại','Sử dụng AAC hiệu quả nếu cần','Cải thiện kỹ năng ngôn ngữ xã hội']),
        'target_age': '18 tháng – 15 tuổi',
        'duration': '45–60 phút/buổi · 2–3 buổi/tuần',
        'video_url': '',
        'order': 2,
    },
    {
        'slug': 'tri-lieu-van-dong',
        'name': 'Trị liệu vận động',
        'icon': '🤸',
        'color': '#D97706',
        'short_desc': 'Cải thiện kỹ năng vận động thô và tinh, điều hòa cảm giác và tăng khả năng tự phục vụ.',
        'intro': 'Trị liệu vận động tại EMY giúp trẻ cải thiện toàn diện các kỹ năng vận động, điều hòa cảm giác và phát triển khả năng tự chăm sóc bản thân trong sinh hoạt hàng ngày.',
        'content': '''<h2>Trị liệu vận động là gì?</h2>
<p>Trị liệu vận động (Occupational Therapy - OT) tập trung giúp trẻ phát triển các kỹ năng cần thiết để thực hiện các hoạt động hàng ngày một cách độc lập và hiệu quả.</p>
<h2>Hai lĩnh vực chính</h2>
<ul>
<li><strong>Vận động thô:</strong> Chạy, nhảy, leo trèo, giữ thăng bằng, phối hợp tay-chân</li>
<li><strong>Vận động tinh:</strong> Cầm bút, cắt, xếp hình, viết, vẽ, cài nút áo</li>
</ul>
<h2>Điều hòa cảm giác</h2>
<p>Nhiều trẻ tự kỷ có vấn đề về xử lý cảm giác. Chương trình OT tại EMY bao gồm liệu pháp tích hợp cảm giác (Sensory Integration) giúp trẻ xử lý thông tin giác quan hiệu quả hơn.</p>
<h2>Kỹ năng tự phục vụ</h2>
<p>EMY tập trung phát triển các kỹ năng sống thiết yếu: ăn uống độc lập, vệ sinh cá nhân, mặc quần áo, chuẩn bị đồ dùng học tập.</p>''',
        'benefits': json.dumps(['Cải thiện phối hợp vận động toàn thân','Phát triển kỹ năng vận động tinh','Điều hòa xử lý cảm giác','Tăng khả năng tự chăm sóc bản thân','Cải thiện tư thế và thăng bằng','Chuẩn bị kỹ năng viết và học đường']),
        'target_age': '2 – 12 tuổi',
        'duration': '45–60 phút/buổi · 2–3 buổi/tuần',
        'video_url': '',
        'order': 3,
    },
    {
        'slug': 'am-nhac-nghe-thuat',
        'name': 'Âm nhạc & Nghệ thuật trị liệu',
        'icon': '🎵',
        'color': '#6A5ACD',
        'short_desc': 'Khai mở cảm xúc, tăng khả năng tập trung và niềm vui học tập qua âm nhạc và nghệ thuật.',
        'intro': 'Âm nhạc và nghệ thuật trị liệu là phương pháp sáng tạo, sử dụng sức mạnh của âm thanh, màu sắc và nghệ thuật để giúp trẻ bày tỏ cảm xúc, phát triển nhận thức và tăng cường kết nối xã hội.',
        'content': '''<h2>Tại sao âm nhạc và nghệ thuật trị liệu?</h2>
<p>Nhiều trẻ tự kỷ không thể biểu đạt cảm xúc qua lời nói nhưng lại phản hồi tốt với âm nhạc và nghệ thuật. Đây là "ngôn ngữ thứ hai" giúp kết nối và phát triển trẻ.</p>
<h2>Âm nhạc trị liệu</h2>
<ul>
<li>Sử dụng nhịp điệu để phát triển ngôn ngữ và giao tiếp</li>
<li>Hát, chơi nhạc cụ giúp cải thiện vận động và phối hợp</li>
<li>Âm nhạc tạo môi trường an toàn để trẻ tương tác xã hội</li>
</ul>
<h2>Nghệ thuật trị liệu</h2>
<ul>
<li>Vẽ, tô màu, nặn đất sét phát triển vận động tinh</li>
<li>Nghệ thuật giúp trẻ biểu đạt cảm xúc không qua lời</li>
<li>Tăng khả năng tập trung, kiên nhẫn và sáng tạo</li>
</ul>
<h2>Tại EMY</h2>
<p>Chương trình được thiết kế bởi các chuyên gia được đào tạo chuyên biệt về âm nhạc trị liệu, kết hợp khoa học và nghệ thuật trong từng buổi học vui vẻ.</p>''',
        'benefits': json.dumps(['Giảm lo lắng và căng thẳng','Phát triển khả năng biểu đạt cảm xúc','Tăng cường tương tác xã hội','Cải thiện kỹ năng giao tiếp','Phát triển sự sáng tạo','Tăng khả năng tập trung và kiên nhẫn']),
        'target_age': '2 tuổi – mọi lứa tuổi',
        'duration': '45–60 phút/buổi · 1–2 buổi/tuần',
        'video_url': '',
        'order': 4,
    },
    {
        'slug': 'giao-duc-hoa-nhap',
        'name': 'Giáo dục hòa nhập',
        'icon': '📚',
        'color': '#E05A3A',
        'short_desc': 'Chuẩn bị cho trẻ bước vào môi trường học tập thông thường với chương trình tiền học đường cá nhân hóa.',
        'intro': 'Chương trình Giáo dục hòa nhập tại EMY giúp trẻ có nhu cầu đặc biệt trang bị đầy đủ kỹ năng học đường, xã hội và cảm xúc để tự tin bước vào lớp học thông thường.',
        'content': '''<h2>Giáo dục hòa nhập là gì?</h2>
<p>Giáo dục hòa nhập là mục tiêu cao nhất của can thiệp sớm — giúp trẻ có nhu cầu đặc biệt học tập cùng các bạn đồng trang lứa trong môi trường học đường thông thường.</p>
<h2>Chương trình tiền tiểu học</h2>
<ul>
<li>Kỹ năng ngồi học, chú ý và làm theo hướng dẫn</li>
<li>Kỹ năng viết, đọc và làm toán cơ bản</li>
<li>Kỹ năng tương tác với bạn bè và thầy cô</li>
<li>Quản lý đồ dùng học tập và thời gian biểu</li>
</ul>
<h2>Hỗ trợ hòa nhập</h2>
<p>EMY cung cấp dịch vụ <strong>Shadow Teacher</strong> (giáo viên hỗ trợ đi kèm) giúp trẻ thích nghi trong những tháng đầu tại trường hòa nhập, đảm bảo quá trình chuyển tiếp suôn sẻ.</p>
<h2>Kết nối với trường học</h2>
<p>Đội ngũ EMY phối hợp chặt chẽ với giáo viên tại trường để xây dựng kế hoạch hỗ trợ phù hợp, điều chỉnh môi trường lớp học và theo dõi tiến trình của trẻ.</p>''',
        'benefits': json.dumps(['Chuẩn bị kỹ năng học đường toàn diện','Phát triển kỹ năng xã hội với bạn đồng trang lứa','Hỗ trợ Shadow Teacher khi cần','Phối hợp với giáo viên tại trường','Tăng sự tự tin và độc lập','Chuẩn bị cảm xúc cho môi trường mới']),
        'target_age': '4 – 8 tuổi',
        'duration': 'Linh hoạt theo kế hoạch IEP',
        'video_url': '',
        'order': 5,
    },
    {
        'slug': 'dao-tao-phu-huynh',
        'name': 'Đào tạo phụ huynh',
        'icon': '👨‍👩‍👧',
        'color': '#3A9BD5',
        'short_desc': 'Hướng dẫn cha mẹ kỹ năng can thiệp tại nhà và kết nối cộng đồng phụ huynh EMY.',
        'intro': 'Cha mẹ là những nhà trị liệu quan trọng nhất của con. Chương trình đào tạo phụ huynh tại EMY giúp gia đình trở thành đối tác tích cực trong hành trình phát triển của trẻ.',
        'content': '''<h2>Tại sao phụ huynh cần được đào tạo?</h2>
<p>Nghiên cứu chứng minh rằng trẻ tiến bộ nhanh hơn đáng kể khi cha mẹ biết cách can thiệp đúng tại nhà. Trẻ ở nhà với gia đình 16-18 giờ mỗi ngày — đây là cơ hội can thiệp vô giá.</p>
<h2>Nội dung chương trình</h2>
<ul>
<li><strong>Hiểu con:</strong> Đặc điểm của tự kỷ, ADHD và các nhu cầu đặc biệt</li>
<li><strong>Kỹ năng ABA tại nhà:</strong> Áp dụng các nguyên tắc hành vi trong sinh hoạt hàng ngày</li>
<li><strong>Giao tiếp với con:</strong> Cách kích thích ngôn ngữ, đọc tín hiệu của trẻ</li>
<li><strong>Quản lý hành vi:</strong> Xử lý tantrum, hành vi thách thức một cách bình tĩnh</li>
<li><strong>Môi trường học tập:</strong> Thiết lập không gian và thói quen tại nhà</li>
</ul>
<h2>Cộng đồng phụ huynh EMY</h2>
<p>Tham gia nhóm phụ huynh EMY để chia sẻ kinh nghiệm, nhận hỗ trợ tâm lý và kết nối với những gia đình có hoàn cảnh tương tự trên toàn TP.HCM.</p>''',
        'benefits': json.dumps(['Hiểu rõ đặc điểm và nhu cầu của con','Áp dụng kỹ năng ABA tại nhà hiệu quả','Giảm stress và lo lắng cho cha mẹ','Cải thiện mối quan hệ gia đình','Kết nối cộng đồng phụ huynh tích cực','Tăng tốc tiến bộ của trẻ tại nhà']),
        'target_age': 'Dành cho phụ huynh có con mọi lứa tuổi',
        'duration': 'Workshop 2–3 giờ · Tư vấn cá nhân 60 phút',
        'video_url': '',
        'order': 6,
    },
]


# ══ PUBLIC ROUTES ═════════════════════════════════════════

@public_bp.route('/')
def index():
    posts    = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).limit(3).all()
    events   = Event.query.filter_by(is_active=True).order_by(Event.start_date).limit(4).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.order).all()
    return render_template('index.html', posts=posts, events=events,
                           services=services, get_media_type=get_media_type)

# ── TRANG DỊCH VỤ CHI TIẾT ────────────────────────────────
@public_bp.route('/dich-vu/<slug>')
def service_detail(slug):
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()

    # Bài viết liên quan (lấy theo category tips)
    related_posts = Post.query.filter_by(is_published=True, category='tips')\
                              .order_by(Post.created_at.desc()).limit(3).all()

    # Các dịch vụ khác
    other_services = Service.query.filter(
        Service.is_active==True, Service.id!=service.id
    ).order_by(Service.order).limit(5).all()

    benefits = []
    if service.benefits:
        try: benefits = json.loads(service.benefits)
        except: pass

    yt_id = get_yt_id(service.video_url) if service.video_url else None

    return render_template('service_detail.html',
        service=service, benefits=benefits,
        related_posts=related_posts, other_services=other_services,
        yt_id=yt_id, get_media_type=get_media_type)

# ── BLOG ─────────────────────────────────────────────────
@public_bp.route('/blog')
def blog():
    page     = request.args.get('page', 1, type=int)
    category = request.args.get('cat', '')
    q        = request.args.get('q', '')
    query    = Post.query.filter_by(is_published=True)
    if category: query = query.filter_by(category=category)
    if q:        query = query.filter(Post.title.ilike(f'%{q}%'))
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('blog.html', posts=posts, category=category, q=q, get_media_type=get_media_type)

@public_bp.route('/blog/<int:post_id>')
def blog_detail(post_id):
    post = Post.query.get_or_404(post_id)
    post.views += 1
    db.session.commit()
    related = Post.query.filter(
        Post.is_published==True, Post.id!=post.id, Post.category==post.category
    ).limit(3).all()
    return render_template('blog_detail.html', post=post, related=related, get_media_type=get_media_type)

@public_bp.route('/lich-khai-giang')
def events():
    events = Event.query.filter_by(is_active=True).order_by(Event.start_date).all()
    return render_template('events.html', events=events)

@public_bp.route('/dang-ky-test', methods=['GET','POST'])
def register_test():
    if request.method == 'POST':
        reg = Registration(
            parent_name=request.form.get('parent_name','').strip(),
            parent_phone=request.form.get('parent_phone','').strip(),
            parent_email=request.form.get('parent_email','').strip(),
            child_name=request.form.get('child_name','').strip(),
            child_age=request.form.get('child_age','').strip(),
            concern=request.form.get('concern','').strip(),
            preferred_date=request.form.get('preferred_date','').strip(),
        )
        db.session.add(reg); db.session.commit()
        flash('✅ Đăng ký thành công! Chúng tôi sẽ liên hệ trong 24h.','success')
        return redirect(url_for('public.register_test'))
    return render_template('register_test.html')

@public_bp.route('/tu-van', methods=['GET','POST'])
def consultation():
    if request.method == 'POST':
        con = Consultation(
            fullname=request.form.get('fullname','').strip(),
            phone=request.form.get('phone','').strip(),
            email=request.form.get('email','').strip(),
            service=request.form.get('service','').strip(),
            message=request.form.get('message','').strip(),
        )
        db.session.add(con); db.session.commit()
        flash('✅ Gửi thành công! Chúng tôi sẽ liên hệ sớm.','success')
        return redirect(url_for('public.consultation'))
    return render_template('consultation.html')

@public_bp.route('/faq')
def faq():
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.order).all()
    return render_template('faq.html', faqs=faqs)


# ══ ADMIN ROUTES ════════════════════════════════════════════

@admin_bp.route('/')
@login_required
def dashboard():
    stats = {
        'students':      Student.query.filter_by(status='active').count(),
        'posts':         Post.query.filter_by(is_published=True).count(),
        'registrations': Registration.query.filter_by(status='pending').count(),
        'consultations': Consultation.query.filter_by(status='new').count(),
    }
    recent_regs = Registration.query.order_by(Registration.created_at.desc()).limit(5).all()
    recent_cons = Consultation.query.order_by(Consultation.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats,
                           recent_regs=recent_regs, recent_cons=recent_cons)

# ── Học sinh ──────────────────────────────────────────────
@admin_bp.route('/hoc-sinh')
@login_required
def students():
    search   = request.args.get('q','')
    query    = Student.query
    if search: query = query.filter(Student.fullname.ilike(f'%{search}%'))
    students = query.order_by(Student.enrolled_at.desc()).all()
    teachers = User.query.filter_by(role='teacher',is_active=True).all()
    return render_template('admin/students.html', students=students, teachers=teachers, search=search)

@admin_bp.route('/hoc-sinh/them', methods=['GET','POST'])
@login_required
def add_student():
    if request.method == 'POST':
        dob_str = request.form.get('dob','')
        dob = datetime.strptime(dob_str,'%Y-%m-%d').date() if dob_str else None
        s = Student(
            fullname=request.form.get('fullname','').strip(), dob=dob,
            gender=request.form.get('gender'),
            diagnosis=request.form.get('diagnosis','').strip(),
            parent_name=request.form.get('parent_name','').strip(),
            parent_phone=request.form.get('parent_phone','').strip(),
            parent_email=request.form.get('parent_email','').strip(),
            address=request.form.get('address','').strip(),
            notes=request.form.get('notes','').strip(),
            teacher_id=request.form.get('teacher_id') or None,
        )
        db.session.add(s); db.session.commit()
        flash(f'✅ Đã thêm học sinh {s.fullname}!','success')
        return redirect(url_for('admin.students'))
    teachers = User.query.filter_by(role='teacher',is_active=True).all()
    return render_template('admin/student_form.html', student=None, teachers=teachers)

@admin_bp.route('/hoc-sinh/sua/<int:id>', methods=['GET','POST'])
@login_required
def edit_student(id):
    s = Student.query.get_or_404(id)
    if request.method == 'POST':
        s.fullname=request.form.get('fullname','').strip()
        s.gender=request.form.get('gender')
        s.diagnosis=request.form.get('diagnosis','').strip()
        s.parent_name=request.form.get('parent_name','').strip()
        s.parent_phone=request.form.get('parent_phone','').strip()
        s.parent_email=request.form.get('parent_email','').strip()
        s.address=request.form.get('address','').strip()
        s.notes=request.form.get('notes','').strip()
        s.teacher_id=request.form.get('teacher_id') or None
        dob_str=request.form.get('dob','')
        if dob_str: s.dob=datetime.strptime(dob_str,'%Y-%m-%d').date()
        db.session.commit()
        flash('✅ Đã cập nhật hồ sơ!','success')
        return redirect(url_for('admin.students'))
    teachers = User.query.filter_by(role='teacher',is_active=True).all()
    return render_template('admin/student_form.html', student=s, teachers=teachers)

@admin_bp.route('/hoc-sinh/xoa/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    s = Student.query.get_or_404(id)
    db.session.delete(s); db.session.commit()
    flash(f'🗑️ Đã xóa học sinh {s.fullname}.','info')
    return redirect(url_for('admin.students'))

# ── Bài viết ──────────────────────────────────────────────
@admin_bp.route('/bai-viet')
@login_required
def posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts, get_media_type=get_media_type)

@admin_bp.route('/bai-viet/them', methods=['GET','POST'])
@login_required
def add_post():
    if request.method == 'POST':
        title    = request.form.get('title','').strip()
        slug     = f"post-{int(datetime.utcnow().timestamp())}"
        media_path = None
        file       = request.files.get('media_file')
        media_url  = request.form.get('media_url','').strip()
        if file and file.filename:
            saved, _ = save_upload(file, 'posts')
            if saved: media_path = saved
        elif media_url:
            media_path = media_url
        p = Post(
            title=title, slug=slug,
            content=request.form.get('content',''),
            summary=request.form.get('summary','').strip(),
            category=request.form.get('category','news'),
            thumbnail=media_path,
            is_published=bool(request.form.get('is_published')),
            author_id=current_user.id,
        )
        db.session.add(p); db.session.commit()
        flash('✅ Đã đăng bài viết!','success')
        return redirect(url_for('admin.posts'))
    return render_template('admin/post_form.html', post=None)

@admin_bp.route('/bai-viet/sua/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    p = Post.query.get_or_404(id)
    if request.method == 'POST':
        p.title=request.form.get('title','').strip()
        p.content=request.form.get('content','')
        p.summary=request.form.get('summary','').strip()
        p.category=request.form.get('category','news')
        p.is_published=bool(request.form.get('is_published'))
        p.updated_at=datetime.utcnow()
        file=request.files.get('media_file')
        media_url=request.form.get('media_url','').strip()
        if request.form.get('remove_media'):
            if p.thumbnail and p.thumbnail.startswith('uploads/'):
                old=os.path.join(current_app.root_path,'static',p.thumbnail)
                if os.path.exists(old): os.remove(old)
            p.thumbnail=None
        elif file and file.filename:
            saved,_=save_upload(file,'posts')
            if saved: p.thumbnail=saved
        elif media_url:
            p.thumbnail=media_url
        db.session.commit()
        flash('✅ Đã cập nhật bài viết!','success')
        return redirect(url_for('admin.posts'))
    return render_template('admin/post_form.html', post=p, get_media_type=get_media_type)

@admin_bp.route('/bai-viet/xoa/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    p = Post.query.get_or_404(id)
    if p.thumbnail and p.thumbnail.startswith('uploads/'):
        old=os.path.join(current_app.root_path,'static',p.thumbnail)
        if os.path.exists(old): os.remove(old)
    db.session.delete(p); db.session.commit()
    flash('🗑️ Đã xóa bài viết.','info')
    return redirect(url_for('admin.posts'))

# ── Đăng ký ───────────────────────────────────────────────
@admin_bp.route('/dang-ky')
@login_required
def registrations():
    status=request.args.get('status','')
    query=Registration.query
    if status: query=query.filter_by(status=status)
    regs=query.order_by(Registration.created_at.desc()).all()
    return render_template('admin/registrations.html', regs=regs, status=status)

@admin_bp.route('/dang-ky/cap-nhat/<int:id>', methods=['POST'])
@login_required
def update_registration(id):
    reg=Registration.query.get_or_404(id)
    reg.status=request.form.get('status',reg.status)
    reg.notes=request.form.get('notes','')
    db.session.commit()
    flash('✅ Đã cập nhật!','success')
    return redirect(url_for('admin.registrations'))

# ── Tiến trình ────────────────────────────────────────────
@admin_bp.route('/tien-trinh')
@login_required
def progress():
    students=Student.query.filter_by(status='active').all()
    return render_template('admin/progress.html', students=students)

@admin_bp.route('/tien-trinh/<int:student_id>')
@login_required
def student_progress(student_id):
    student=Student.query.get_or_404(student_id)
    logs=Progress.query.filter_by(student_id=student_id).order_by(Progress.date.desc()).all()
    today=datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/student_progress.html', student=student, logs=logs, today=today)

@admin_bp.route('/tien-trinh/them/<int:student_id>', methods=['POST'])
@login_required
def add_progress(student_id):
    p=Progress(
        student_id=student_id, teacher_id=current_user.id,
        date=datetime.strptime(request.form.get('date'),'%Y-%m-%d').date(),
        session_type=request.form.get('session_type','').strip(),
        goals=request.form.get('goals','').strip(),
        achievements=request.form.get('achievements','').strip(),
        rating=int(request.form.get('rating',3)),
        next_steps=request.form.get('next_steps','').strip(),
    )
    db.session.add(p); db.session.commit()
    flash('✅ Đã ghi nhận tiến trình!','success')
    return redirect(url_for('admin.student_progress', student_id=student_id))

# ── Tài khoản ─────────────────────────────────────────────
@admin_bp.route('/tai-khoan')
@login_required
@admin_required
def accounts():
    users=User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/accounts.html', users=users)

@admin_bp.route('/tai-khoan/them', methods=['GET','POST'])
@login_required
@admin_required
def add_account():
    if request.method == 'POST':
        u=User(
            fullname=request.form.get('fullname','').strip(),
            email=request.form.get('email','').strip(),
            password_hash=generate_password_hash(request.form.get('password')),
            role=request.form.get('role','teacher'),
        )
        db.session.add(u); db.session.commit()
        flash(f'✅ Đã tạo tài khoản {u.email}!','success')
        return redirect(url_for('admin.accounts'))
    return render_template('admin/account_form.html', user=None)
