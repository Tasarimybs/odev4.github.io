from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

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
        p1 = Product(name='Akıllı Telefon X1', description='OLED ekran...', price=24999, image='', category_id=1)
        p2 = Product(name='Pro Kulaklık', description='ANC özellikli...', price=4799, image='', category_id=2)
        p3 = Product(name='Ultra Laptop', description='Yüksek performans...', price=38500, image='', category_id=3)
        p4 = Product(name='4K Smart TV', description='Gelişmiş görüntü...', price=19899, image='', category_id=4)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

    # Kampanya
    if not Campaign.query.first():
        now = datetime.utcnow()
        c1 = Campaign(
            title="24 Saatlik İndirim",
            subtitle="Seçili ürünlerde %20 indirim",
            percent_discount=20,
            starts_at=now,
            ends_at=now + timedelta(days=1)
        )
        db.session.add(c1)
        db.session.commit()

        # İlk iki ürünü kampanyaya ekle
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
    return render_template(
        "home.html",
        urunler=Product.query.all(),
        kategoriler=Category.query.all(),
        sepet_urun_sayisi=len(get_sepet())
    )


@app.route("/kampanyalar")
def kampanyalar():
    active = Campaign.query.filter_by(active=True).all()
    kamp_list = []

    for k in active:
        kamp_list.append({
            "id": k.id,
            "title": k.title,
            "subtitle": k.subtitle,
            "image": k.image,
            "ends_at": k.ends_at.isoformat() if k.ends_at else None
        })

    return render_template("kampanyalar.html",
                           kampanyalar=kamp_list,
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
        applied_info = None

    return render_template(
        "sepet.html",
        sepet_urunler=db_items,
        subtotal=subtotal,
        indirim=best_discount,
        toplam=toplam,
        sepet_urun_sayisi=len(ids),
        applied_info=applied_info
    )


@app.route("/sepete-ekle", methods=["POST"])
def sepete_ekle():
    pid = int(request.form["urun_id"])
    sepet = get_sepet()

    if pid not in sepet:
        sepet.append(pid)

    set_sepet(sepet)
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
        p1 = Product(name='Akıllı Telefon X1', description='OLED...', price=24999, image='', category_id=1)
        p2 = Product(name='Pro Kulaklık', description='ANC...', price=4799, image='', category_id=2)
        p3 = Product(name='Ultra Laptop', description='Laptop...', price=38500, image='', category_id=3)
        p4 = Product(name='4K Smart TV', description='TV...', price=19899, image='', category_id=4)
        db.session.add_all([p1, p2, p3, p4])
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



