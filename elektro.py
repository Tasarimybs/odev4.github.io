from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

# -------------------------------------------------------
# APP & DATABASE SETUP
# -------------------------------------------------------

app = Flask(__name__, instance_path=os.path.join(os.path.dirname(__file__), 'instance'))
app.secret_key = "supersecret"

db_path = os.path.join(app.instance_path, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------------------------------------
# MODELLER
# -------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class AboutPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))


# -------------------------------------------------------
# KAMPANYA MODELLERİ
# -------------------------------------------------------

campaign_products = db.Table(
    'campaign_products',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(400))
    image = db.Column(db.String(400))
    discount_text = db.Column(db.String(100))
    percent_discount = db.Column(db.Integer)
    min_cart_total = db.Column(db.Integer)
    free_shipping = db.Column(db.Boolean, default=False)
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)

    products = db.relationship(
        'Product',
        secondary=campaign_products,
        backref=db.backref('campaigns', lazy='dynamic')
    )


# -------------------------------------------------------
# SESSION SEPET
# -------------------------------------------------------

def get_sepet():
    return session.get("sepet", [])

def set_sepet(data):
    session["sepet"] = data


# -------------------------------------------------------
# SEED & DATABASE INITIALIZE
# -------------------------------------------------------

def create_tables_and_seed():
    db.create_all()

    # İlk kategori ekleme
    if not Category.query.first():
        cat1 = Category(name='Telefonlar', image='url1')
        cat2 = Category(name='Kulaklıklar', image='url2')
        cat3 = Category(name='Tabletler', image='url3')
        cat4 = Category(name='Televizyonlar', image='url4')
        db.session.add_all([cat1, cat2, cat3, cat4])
        db.session.commit()

    # İlk ürünler
    if not Product.query.first():
        # Telefon Serisi (X1, X2, X3, X4)
        p1 = Product(name='Akıllı Telefon X1', description='6.7" OLED ekran, 128GB depolama, 5000mAh batarya, 50MP kamera', price=24999, image='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80', category_id=1)
        p2 = Product(name='Akıllı Telefon X2 Pro', description='6.8" AMOLED ekran, 256GB depolama, 5500mAh batarya, 108MP kamera, 120Hz', price=34999, image='https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800&q=80', category_id=1)
        p3 = Product(name='Akıllı Telefon X3 Ultra', description='6.9" Dynamic AMOLED ekran, 512GB depolama, 6000mAh batarya, 200MP kamera', price=44999, image='https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&q=80', category_id=1)
        p4 = Product(name='Akıllı Telefon X4 Max', description='7.0" LTPO AMOLED ekran, 1TB depolama, 6500mAh batarya, AI destekli 200MP kamera', price=54999, image='https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80', category_id=1)
        
        # Kulaklıklar
        p5 = Product(name='Pro Kulaklık ANC', description='Aktif gürültü engelleme, 30 saat batarya, premium ses kalitesi', price=4799, image='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80', category_id=2)
        p6 = Product(name='Gaming Kulaklık RGB', description='7.1 surround ses, RGB aydınlatma, rahat kulak yastıkları', price=3299, image='https://images.unsplash.com/photo-1487215078519-e21cc028cb29?w=800&q=80', category_id=2)
        
        # Laptop & Tabletler
        p7 = Product(name='Ultra Laptop Pro', description='15.6" 4K ekran, Intel i9, 32GB RAM, RTX 4070, 1TB SSD', price=38500, image='https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80', category_id=3)
        p8 = Product(name='Pro Tablet 12"', description='12.9" Retina ekran, M2 chip, 256GB, Apple Pencil desteği', price=28999, image='https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&q=80', category_id=3)
        
        # Televizyonlar
        p9 = Product(name='4K Smart TV 55"', description='55" QLED ekran, HDR10+, 120Hz, Smart TV özellikleri', price=19899, image='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&q=80', category_id=4)
        p10 = Product(name='8K Smart TV 65"', description='65" Neo QLED ekran, 8K AI upscaling, Dolby Atmos', price=45999, image='https://images.unsplash.com/photo-1601944177325-f8867652837f?w=800&q=80', category_id=4)
        
        db.session.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
        db.session.commit()

    # Kampanya
    if not Campaign.query.first():
        now = datetime.utcnow()
        c1 = Campaign(
            title="24 Saatlik İndirim",
            subtitle="Seçili ürünlerde %20 indirim",
            percent_discount=20,
            image='https://images.unsplash.com/photo-1607082349566-187342175e2f?w=600&q=80',
            starts_at=now,
            ends_at=now + timedelta(days=1)
        )
        c2 = Campaign(
            title="Teknoloji Festivali",
            subtitle="Tüm elektronik ürünlerde büyük fırsatlar",
            percent_discount=30,
            image='https://images.unsplash.com/photo-1498049794561-7780e7231661?w=600&q=80',
            min_cart_total=1000,
            starts_at=now,
            ends_at=now + timedelta(days=7)
        )
        c3 = Campaign(
            title="Yaz İndirimi",
            subtitle="Telefon ve tablet modellerinde özel fiyatlar",
            percent_discount=25,
            image='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&q=80',
            min_cart_total=500,
            starts_at=now,
            ends_at=now + timedelta(days=5)
        )
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # İlk iki ürünü kampanyaya ekle
        products = Product.query.limit(2).all()
        c1.products.extend(products)
        db.session.commit()


with app.app_context():
    create_tables_and_seed()


# -------------------------------------------------------
# KULLANıCı ROTLARI (AUTH)
# -------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")
        
        if not name or not email or not password:
            flash("Tüm alanları doldurmanız gerekiyor!", "error")
            return redirect(url_for("register"))
        
        if password != password_confirm:
            flash("Şifreler eşleşmiyor!", "error")
            return redirect(url_for("register"))
        
        if User.query.filter_by(email=email).first():
            flash("Bu e-posta adresi zaten kullanılıyor!", "error")
            return redirect(url_for("register"))
        
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash("Kayıt başarılı! Lütfen giriş yapınız.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html", sepet_urun_sayisi=len(get_sepet()))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash(f"Hoş geldiniz, {user.name}!", "success")
            return redirect(url_for("home"))
        else:
            flash("E-posta veya şifre hatalı!", "error")
    
    return render_template("login.html", sepet_urun_sayisi=len(get_sepet()))


@app.route("/profil")
def profil():
    user_id = session.get("user_id")
    if not user_id:
        flash("Lütfen önce giriş yapınız!", "error")
        return redirect(url_for("login"))
    
    user = User.query.get(user_id)
    return render_template("profil.html", user=user, sepet_urun_sayisi=len(get_sepet()))


@app.route("/profil-guncelle", methods=["POST"])
def profil_guncelle():
    user_id = session.get("user_id")
    if not user_id:
        flash("Lütfen önce giriş yapınız!", "error")
        return redirect(url_for("login"))
    
    user = User.query.get(user_id)
    user.name = request.form.get("name", user.name)
    user.phone = request.form.get("phone", user.phone)
    user.address = request.form.get("address", user.address)
    
    db.session.commit()
    flash("Profil başarıyla güncellendi!", "success")
    return redirect(url_for("profil"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız!", "success")
    return redirect(url_for("home"))


# -------------------------------------------------------
# SAYFA ROTLARI
# -------------------------------------------------------

@app.route("/")
def home():
    return render_template(
        "home.html",
        urunler=Product.query.all(),
        kategoriler=Category.query.all(),
        sepet_urun_sayisi=len(get_sepet())
    )


@app.route("/ara")
def ara():
    q = request.args.get("q", "").strip()
    if q:
        urunler = Product.query.filter(
            (Product.name.ilike(f"%{q}%")) | 
            (Product.description.ilike(f"%{q}%"))
        ).all()
    else:
        urunler = []
    
    return render_template(
        "home.html",
        urunler=urunler,
        kategoriler=Category.query.all(),
        sepet_urun_sayisi=len(get_sepet()),
        arama_sorgusu=q
    )


@app.route("/kampanyalar")
def kampanyalar():
    active = Campaign.query.filter_by(active=True).all()
    kamp_list = []
    now = datetime.utcnow()

    for k in active:
        ends_at = k.ends_at
        kamp_list.append({
            "id": k.id,
            "title": k.title,
            "subtitle": k.subtitle,
            "image": k.image,
            "percent_discount": k.percent_discount,
            "min_cart_total": k.min_cart_total,
            "ends_at": ends_at.isoformat() if ends_at else None,
            "is_24h": bool(ends_at and (ends_at - now) <= timedelta(hours=24))
        })

    # Telefon ürünlerini getir
    telefon_urunler = Product.query.filter(
        (Product.name.ilike('%telefon%')) | 
        (Product.name.ilike('%phone%'))
    ).all()

    return render_template("kampanyalar.html",
                           kampanyalar=kamp_list,
                           urunler=telefon_urunler,
                           sepet_urun_sayisi=len(get_sepet()))


@app.route("/hakkimizda")
def hakkimizda():
    return render_template("hakkimizda.html",
                           about=AboutPage.query.first(),
                           sepet_urun_sayisi=len(get_sepet()))


@app.route("/iletisim", methods=["GET", "POST"])
def iletisim():
    contact = ContactInfo.query.first()

    if request.method == "POST":
        db.session.add(Message(
            name=request.form["name"],
            email=request.form["email"],
            message=request.form["message"]
        ))
        db.session.commit()
        return redirect(url_for("iletisim"))

    return render_template("iletisim.html",
                           contact=contact,
                           sepet_urun_sayisi=len(get_sepet()))


@app.route("/urun/<int:urun_id>")
def urun_detay(urun_id):
    urun = Product.query.get_or_404(urun_id)
    
    # Aynı kategoriden benzer ürünler
    benzer_urunler = Product.query.filter(
        Product.category_id == urun.category_id,
        Product.id != urun_id
    ).limit(4).all()
    
    return render_template("urun_detay.html",
                           urun=urun,
                           benzer_urunler=benzer_urunler,
                           sepet_urun_sayisi=len(get_sepet()))


# -------------------------------------------------------
# SEPET (SESSION)
# -------------------------------------------------------

@app.route("/sepet")
def sepet():
    ids = get_sepet()
    db_items = Product.query.filter(Product.id.in_(ids)).all()

    subtotal = sum([i.price for i in db_items])
    sepet_ids = [i.id for i in db_items]

    now = datetime.utcnow()
    applicable = []

    for kamp in Campaign.query.filter_by(active=True).all():

        if kamp.starts_at and kamp.starts_at > now:
            continue
        if kamp.ends_at and kamp.ends_at < now:
            continue

        applies = False

        if kamp.min_cart_total and subtotal >= kamp.min_cart_total:
            applies = True

        if kamp.products:
            k_products = [p.id for p in kamp.products]
            if any(pid in k_products for pid in sepet_ids):
                applies = True

        if applies:
            applicable.append(kamp)

    best_discount = 0
    applied_campaign = None
    for k in applicable:
        if k.percent_discount:
            discount = subtotal * (k.percent_discount / 100)
            if discount > best_discount:
                best_discount = discount
                applied_campaign = k

    toplam = subtotal - best_discount

    if applied_campaign:
        applied_info = {
            'campaign': applied_campaign.title,
            'discount_amount': int(best_discount)
        }
    else:
        applied_info = {}

    # Benzer ürünler öner
    similar_products = []
    if db_items:
        first_cat = db_items[0].category_id
        similar_products = Product.query.filter(
            Product.category_id == first_cat,
            ~Product.id.in_(sepet_ids)
        ).limit(3).all()

    return render_template(
        "sepet.html",
        sepet_urunler=db_items,
        subtotal=subtotal,
        indirim=best_discount,
        toplam_fiyat=int(toplam),
        sepet_urun_sayisi=len(ids),
        applied_info=applied_info,
        similar_products=similar_products
    )


@app.route("/sepete-ekle", methods=["POST"])
def sepete_ekle():
    pid = int(request.form["urun_id"])
    sepet = get_sepet()

    if pid not in sepet:
        sepet.append(pid)
        urun = Product.query.get(pid)
        if urun:
            flash(f'{urun.name} sepetinize eklendi!', 'success')
    else:
        flash('Bu ürün zaten sepetinizde!', 'info')

    set_sepet(sepet)
    
    # Referrer'a göre yönlendirme
    referrer = request.referrer
    if referrer and '/urun/' in referrer:
        return redirect(referrer)
    return redirect(url_for("home"))


@app.route("/sepetten-sil", methods=["POST"])
def sepetten_sil():
    pid = int(request.form["urun_id"])
    sepet = get_sepet()

    if pid in sepet:
        sepet.remove(pid)

    set_sepet(sepet)
    return redirect(url_for("sepet"))


# -------------------------------------------------------
# ADMIN PANEL
# -------------------------------------------------------

@app.route("/admin")
def admin():
    return render_template("admin.html",
                           urunler=Product.query.all(),
                           kategoriler=Category.query.all(),
                           kampanyalar=Campaign.query.all())


# -------------------------------------------------------
# RUN
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__, instance_path=os.path.join(os.path.dirname(__file__), 'instance'))
app.secret_key = "supersecret"

db_path = os.path.join(app.instance_path, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# -------------------------------------------------------
# MODELLER
# -------------------------------------------------------

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class AboutPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))


from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__, instance_path=os.path.join(os.path.dirname(__file__), 'instance'))
app.secret_key = "supersecret"

db_path = os.path.join(app.instance_path, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# -------------------------------------------------------
# MODELLER
# -------------------------------------------------------

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    products = db.relationship('Product', backref='category', lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)


class AboutPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)


class ContactInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))


campaign_products = db.Table(
    'campaign_products',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaign.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(400))
    image = db.Column(db.String(400))
    discount_text = db.Column(db.String(100))
    percent_discount = db.Column(db.Integer, nullable=True)
    min_cart_total = db.Column(db.Integer, nullable=True)
    free_shipping = db.Column(db.Boolean, default=False)
    starts_at = db.Column(db.DateTime, nullable=True)
    ends_at = db.Column(db.DateTime, nullable=True)
    active = db.Column(db.Boolean, default=True)
    products = db.relationship(
        'Product', secondary=campaign_products,
        backref=db.backref('campaigns', lazy='dynamic')
    )


# -------------------------------------------------------
# SESSION SEPET
# -------------------------------------------------------

def get_sepet():
    return session.get("sepet", [])

def set_sepet(data):
    session["sepet"] = data


# -------------------------------------------------------
# SEED ve TABLO OLUŞTURMA
# -------------------------------------------------------

def create_tables_and_seed():
    db.create_all()

    # Kategoriler
    if not Category.query.first():
        cat1 = Category(name='Telefonlar', image='url1')
        cat2 = Category(name='Kulaklıklar', image='url2')
        cat3 = Category(name='Tabletler', image='url3')
        cat4 = Category(name='Televizyonlar', image='url4')
        db.session.add_all([cat1, cat2, cat3, cat4])
        db.session.commit()

    # Ürünler
    if not Product.query.first():
        # Telefon Serisi (X1, X2, X3, X4)
        p1 = Product(name='Akıllı Telefon X1', description='6.7" OLED ekran, 128GB depolama, 5000mAh batarya, 50MP kamera', price=24999, image='https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80', category_id=1)
        p2 = Product(name='Akıllı Telefon X2 Pro', description='6.8" AMOLED ekran, 256GB depolama, 5500mAh batarya, 108MP kamera, 120Hz', price=34999, image='https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800&q=80', category_id=1)
        p3 = Product(name='Akıllı Telefon X3 Ultra', description='6.9" Dynamic AMOLED ekran, 512GB depolama, 6000mAh batarya, 200MP kamera', price=44999, image='https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&q=80', category_id=1)
        p4 = Product(name='Akıllı Telefon X4 Max', description='7.0" LTPO AMOLED ekran, 1TB depolama, 6500mAh batarya, AI destekli 200MP kamera', price=54999, image='https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80', category_id=1)
        
        # Kulaklıklar
        p5 = Product(name='Pro Kulaklık ANC', description='Aktif gürültü engelleme, 30 saat batarya, premium ses kalitesi', price=4799, image='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80', category_id=2)
        p6 = Product(name='Gaming Kulaklık RGB', description='7.1 surround ses, RGB aydınlatma, rahat kulak yastıkları', price=3299, image='https://images.unsplash.com/photo-1487215078519-e21cc028cb89?w=800&q=80', category_id=2)
        
        # Laptop & Tabletler
        p7 = Product(name='Ultra Laptop Pro', description='15.6" 4K ekran, Intel i9, 32GB RAM, RTX 4070, 1TB SSD', price=38500, image='https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80', category_id=3)
        p8 = Product(name='Pro Tablet 12"', description='12.9" Retina ekran, M2 chip, 256GB, Apple Pencil desteği', price=28999, image='https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&q=80', category_id=3)
        
        # Televizyonlar
        p9 = Product(name='4K Smart TV 55"', description='55" QLED ekran, HDR10+, 120Hz, Smart TV özellikleri', price=19899, image='https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&q=80', category_id=4)
        p10 = Product(name='8K Smart TV 65"', description='65" Neo QLED ekran, 8K AI upscaling, Dolby Atmos', price=45999, image='https://images.unsplash.com/photo-1601944177325-f8867652837f?w=800&q=80', category_id=4)
        
        db.session.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10])
        db.session.commit()

    # Kampanyalar
    if not Campaign.query.first():
        now = datetime.utcnow()
        c1 = Campaign(title='24 Saatlik İndirim', subtitle='Seçili ürünler %20', percent_discount=20,
                      starts_at=now, ends_at=now+timedelta(days=1))
        db.session.add(c1)
        db.session.commit()

        products = Product.query.limit(2).all()
        c1.products.extend(products)
        db.session.commit()


with app.app_context():
    create_tables_and_seed()


# -------------------------------------------------------
# SAYFA ROTLARI
# -------------------------------------------------------

@app.route("/")
def home():
    urunler = Product.query.all()
    kategoriler = Category.query.all()
    return render_template("home.html",
                           urunler=urunler,
                           kategoriler=kategoriler,
                           sepet_urun_sayisi=len(get_sepet()))


@app.route("/kampanyalar")
def kampanyalar():
    sepet_urun_sayisi = len(get_sepet())
    kamp_list = []

    for k in Campaign.query.filter_by(active=True).all():
        kamp_list.append({
            "id": k.id,
            "title": k.title,
            "subtitle": k.subtitle,
            "image": k.image,
            "ends_at": k.ends_at.isoformat() if k.ends_at else None
        })

    return render_template("kampanyalar.html",
                           kampanyalar=kamp_list,
                           sepet_urun_sayisi=sepet_urun_sayisi)


@app.route("/hakkimizda")
def hakkimizda():
    about = AboutPage.query.first()
    return render_template("hakkimizda.html",
                           about=about,
                           sepet_urun_sayisi=len(get_sepet()))


@app.route("/iletisim", methods=["GET", "POST"])
def iletisim():
    contact = ContactInfo.query.first()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        db.session.add(Message(name=name, email=email, message=message))
        db.session.commit()
        return redirect(url_for("iletisim"))

    return render_template("iletisim.html",
                           contact=contact,
                           sepet_urun_sayisi=len(get_sepet()))


# -------------------------------------------------------
# SEPET (SESSION)
# -------------------------------------------------------

@app.route("/sepet")
def sepet():
    ids = get_sepet()
    db_items = Product.query.filter(Product.id.in_(ids)).all()
    
    subtotal = sum([i.price for i in db_items])
    sepet_ids = [i.id for i in db_items]

    now = datetime.utcnow()
    applicable = []

    for kamp in Campaign.query.filter_by(active=True).all():
        if kamp.starts_at and kamp.starts_at > now: continue
        if kamp.ends_at and kamp.ends_at < now: continue

        applies = False

        if kamp.min_cart_total and subtotal >= kamp.min_cart_total:
            applies = True

        if kamp.products:
            k_products = [p.id for p in kamp.products]
            if any(pid in k_products for pid in sepet_ids):
                applies = True

        if applies:
            applicable.append(kamp)

    best_discount = 0

    for k in applicable:
        if k.percent_discount:
            disc = subtotal * (k.percent_discount / 100)
            best_discount = max(best_discount, disc)

    toplam = subtotal - best_discount

    return render_template("sepet.html",
                           sepet_urunler=db_items,
                           subtotal=subtotal,
                           indirim=best_discount,
                           toplam=toplam,
                           sepet_urun_sayisi=len(ids))


@app.route("/sepete-ekle", methods=["POST"])
def sepete_ekle():
    pid = int(request.form.get("urun_id"))
    sepet = get_sepet()
    if pid not in sepet:
        sepet.append(pid)
    set_sepet(sepet)
    return redirect(url_for("home"))


@app.route("/sepetten-sil", methods=["POST"])
def sepetten_sil():
    pid = int(request.form.get("urun_id"))
    sepet = get_sepet()
    if pid in sepet:
        sepet.remove(pid)
    set_sepet(sepet)
    return redirect(url_for("sepet"))


# -------------------------------------------------------
# ADMIN PANEL
# -------------------------------------------------------

@app.route("/admin")
def admin():
    return render_template("admin.html",
                           urunler=Product.query.all(),
                           kategoriler=Category.query.all(),
                           kampanyalar=Campaign.query.all())


# -------------------------------------------------------
# RUN
# -------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
# SESSION SEPET
# -------------------------------------------------------

def get_sepet():
    return session.get("sepet", [])

def set_sepet(data):
    session["sepet"] = data


# -------------------------------------------------------
# SEED ve TABLO OLUŞTURMA
# -------------------------------------------------------

def create_tables_and_seed():
    db.create_all()



