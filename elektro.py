
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


import os
app = Flask(__name__, instance_path=os.path.join(os.path.dirname(__file__), 'instance'))
db_path = os.path.join(app.instance_path, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELLER
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# VERİTABANI OLUŞTURMA
with app.app_context():
    db.create_all()
    # Kategoriler ve ürünler yoksa ekle
    if not Category.query.first():
        kategoriler = [
            Category(name='Telefon'),
            Category(name='Bilgisayar'),
            Category(name='TV'),
            Category(name='Aksesuar'),
        ]
        db.session.add_all(kategoriler)
        db.session.commit()
    if not Product.query.first():
        urunler = [
            Product(name='Akıllı Telefon X1 Pro', description='Yüksek performanslı akıllı telefon.', price=24999, image='https://lh3.googleusercontent.com/aida-public/AB6AXuCcVVcweYe_-8dWr4Ju4pIKIclz_KwZ_74gLJh3-pJ92s_6_OX9CFKygd_6Qp6tH9YKqNTKGHJCl5OpeWmfg5s051NpjWDGXPivfSSn1FWB-f1rpzMKy0ausUpmQkGyBhd9NI1g6M_5iX2bGUJ-vgFwQo1GJb_YXTmQNWNf4WaFxBRMXAdagb6bWMiTTBUb7nH6iALM_K3jSei5-Vqd-5crRk36WbJbUqJ9N684pf_ECHhs-6ijH3smvcCY4hw13tywp4LqQ6FvLMg', category_id=1),
            Product(name='Kablosuz Kulaklık', description='Yüksek kaliteli ses deneyimi.', price=2999, image='https://lh3.googleusercontent.com/aida-public/AB6AXuBWhGoPB2kQvonnPa-mcp1oMJVJ1MhyOnE0L0_678iewpWfv5eMEDO1FHfGNk1lRWaBEOoVVC6X18poNbvk2FRggQ59Jih_hNNHrYvHXtL44BXKWm_FuAUU89bqfbVzV2PEzhkZs-1hcmedArWSC98W198xOxXg06rvjK_WeHzDvOPkMj1uJUyojRey6AcGkyR82k2umUxW9CbHtk_axAXUPEl1oMv7hZpDid6dzKPQ9wo-HnTk2rQDOUAAJLgG9QKGbz9sSU0UpJc', category_id=4),
            Product(name='Tablet 10"', description='Geniş ekranlı tablet.', price=8999, image='https://lh3.googleusercontent.com/aida-public/AB6AXuAtUkdOMdTn2avl33rU5SHYT6htpVcbTbm3uOdA1Q0hFn6hV2vn03g0ZkpiI2wBB0GM_QpBvMV6AmCQ2UFZ4MtieSG1sQx8VYtGBQbbPGVHoo9wkENpzLQOj5QJXZdo-tV6RAdaxGfP8dwx1PGiiXwykW6W2lKBj5_nWa6ngX5Urcv6lL0tKqtQFEUkPHpY9bJ8v6X3jQdcSaNtkb0fePzH1qDEQk8N9bq9CEIIUgkhcrMMslMOUIwsU6ctSKFNHgKOed0chU9yDc4', category_id=2),
            Product(name='4K Smart TV 55"', description='Ultra HD çözünürlükte akıllı TV.', price=34999, image='https://lh3.googleusercontent.com/aida-public/AB6AXuBQGTyHhe7xUl-5-S3yrBjLbQgM1OOTe-bOoIjq4qluTT5rsHTpQBOCd_WOFsOFMImGRd_IurN-TS2Ugms-ZF8OlZP5jyKMVJ1px2cTdvj6BNA7whBtvTD4bjWLl8lAsCc_GpWpMovcwU7BZGRYqm3hUd6mKjVLbFaBxJHGITVp1-FvACd_35QG-ECy1Otz8pQVHOm8DixfU4bBWJ7PZ0cVzd9DBkW5iJ9mceb51Ci0fXrV1h4eJ28dJIDwlxiFKj6Tlxi_rK38X8E', category_id=3),
            Product(name='Ultra Laptop M3', description='Yüksek performanslı dizüstü bilgisayar.', price=42999, image='https://lh3.googleusercontent.com/aida-public/AB6AXuAq8UX7BTFPNdpVSWYUP2GgEQVktgLvB6XdxoDTpE9gm7l2zhYlYk9zkpKzo1NN-r6vdtXc6tpss9HtEHPorTsG6aJwp_2XoK7mgMpLrnrNMolh_iR5A86fMpUB96bZuVDN8XMDN4yMW8mCBIuBg05KQK-gb_sxrV2KcW7dxHcZ1QZm6qTHFTAnesKNIhHOwKupAVim_7IR5LDgLZjjHIAXLiFqNgcUjTd8PQyaGyHKqaVARGo7e8_bmv4hGIpeUQfq5iFDJmL4M0I', category_id=2),
            Product(name='Akıllı Saat Series 8', description='Sağlık ve spor için akıllı saat.', price=5999, image='https://lh3.googleusercontent.com/aida-public/AB6AXuCNkURSLEVHrYxZkBzFczfXHSzLlf5ulYfq6ee8OEwAI3pT69lTjNQOxQDzHNsnEzl7f9QQaO4qHBI9OwGPU9vBBUPFmmNdkVsRCB1-thLAz-r_4fVm3vWMjBro1eAB0TZcwLzad4foaQh_96UZI2nh-xaXD1SLIu6TyK2Bn7FSE2dv5lLBDZIT0AmWAEIVktSYa3T0TFihmAuIqvXzkFa4I7UzddTBBH7lJNsIFfs-FroY9XZ6PcMAKyCIEXFjmiTAOkt1T005YWo', category_id=4),
        ]
        db.session.add_all(urunler)
        db.session.commit()

# ROUTES
@app.route("/")
def home():
    sepet_urun_sayisi = CartItem.query.count()
    urunler = Product.query.all()
    return render_template("home.html", urunler=urunler, sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/hakkimizda")
def hakkimizda():
    sepet_urun_sayisi = CartItem.query.count()
    return render_template("hakkimizda.html", sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/iletisim", methods=["GET", "POST"])
def iletisim():
    sepet_urun_sayisi = CartItem.query.count()
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        msg = Message(name=name, email=email, message=message)
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for("iletisim"))
    return render_template("iletisim.html", sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/sepet", methods=["GET", "POST"])
def sepet_sayfa():
    sepet_urun_sayisi = CartItem.query.count()
    sepet_urunler = CartItem.query.all()
    toplam_fiyat = sum([item.product.price for item in sepet_urunler if item.product])
    return render_template("sepet.html", sepet_urunler=[item.product for item in sepet_urunler if item.product], toplam_fiyat=toplam_fiyat, sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/sepete-ekle", methods=["POST"])
def sepete_ekle():
    urun_id = int(request.form.get("urun_id"))
    urun = Product.query.get(urun_id)
    if urun:
        db.session.add(CartItem(product_id=urun.id))
        db.session.commit()
    return redirect(url_for("sepet_sayfa"))

@app.route("/sepetten-sil", methods=["POST"])
def sepetten_sil():
    urun_id = int(request.form.get("urun_id"))
    item = CartItem.query.filter_by(product_id=urun_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("sepet_sayfa"))

# ADMIN PANEL
@app.route("/admin", methods=["GET", "POST"])
def admin():
    kategoriler = Category.query.all()
    urunler = Product.query.all()
    return render_template("admin.html", kategoriler=kategoriler, urunler=urunler)

@app.route("/admin/urun-ekle", methods=["POST"])
def admin_urun_ekle():
    name = request.form.get("name")
    description = request.form.get("description")
    price = int(request.form.get("price"))
    image = request.form.get("image")
    category_id = int(request.form.get("category_id"))
    urun = Product(name=name, description=description, price=price, image=image, category_id=category_id)
    db.session.add(urun)
    db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/urun-guncelle", methods=["POST"])
def admin_urun_guncelle():
    urun_id = int(request.form.get("urun_id"))
    price = int(request.form.get("price"))
    urun = Product.query.get(urun_id)
    if urun:
        urun.price = price
        db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/urun-sil", methods=["POST"])
def admin_urun_sil():
    urun_id = int(request.form.get("urun_id"))
    urun = Product.query.get(urun_id)
    if urun:
        db.session.delete(urun)
        db.session.commit()
    return redirect(url_for("admin"))

@app.route("/admin/mesajlar")
def admin_mesajlar():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template("adminmesaj.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/")
def home():
    sepet_urun_sayisi = len(sepet)
    return render_template("home.html", urunler=urunler, sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/hakkimizda")
def hakkimizda():
    sepet_urun_sayisi = len(sepet)
    return render_template("hakkimizda.html", sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/iletisim", methods=["GET", "POST"])
def iletisim():
    sepet_urun_sayisi = len(sepet)
    if request.method == "POST":
        # Formdan gelen verileri işleyebilirsiniz
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        # Burada mesajı kaydedebilir veya e-posta gönderebilirsiniz
        return redirect(url_for("iletisim"))
    return render_template("iletisim.html", sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/sepet", methods=["GET", "POST"])
def sepet_sayfa():
    sepet_urun_sayisi = len(sepet)
    toplam_fiyat = sum([urun['fiyat'] for urun in sepet])
    return render_template("sepet.html", sepet_urunler=sepet, toplam_fiyat=toplam_fiyat, sepet_urun_sayisi=sepet_urun_sayisi)

@app.route("/sepete-ekle", methods=["POST"])
def sepete_ekle():
    urun_id = int(request.form.get("urun_id"))
    urun = next((u for u in urunler if u['id'] == urun_id), None)
    if urun:
        sepet.append(urun)
    return redirect(url_for("sepet_sayfa"))

@app.route("/sepetten-sil", methods=["POST"])
def sepetten_sil():
    urun_id = int(request.form.get("urun_id"))
    global sepet
    sepet = [u for u in sepet if u['id'] != urun_id]
    return redirect(url_for("sepet_sayfa"))

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
## from flask_login import LoginManager, UserMixin
from collections import namedtuple

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Veritabanı ayarı
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# -----------------------------
# MODELLER
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(300))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

# Sayfa içerikleri (Hakkımızda, İletişim)
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


# -----------------------------
# VERİTABANINI OLUŞTUR + SEED
# -----------------------------
def create_tables_and_seed():
    db.create_all()

    if not Category.query.first():
        cat1 = Category(name='Telefonlar', image='url1')
        cat2 = Category(name='Kulaklıklar', image='url2')
        cat3 = Category(name='Tabletler', image='url3')
        cat4 = Category(name='Televizyonlar', image='url4')
        db.session.add_all([cat1, cat2, cat3, cat4])
        db.session.commit()

    if not Product.query.first():
        p1 = Product(name='Akıllı Telefon X1', description='...', price=24999, image='url', category_id=1)
        p2 = Product(name='Pro Kulaklık', description='...', price=4799, image='url', category_id=2)
        p3 = Product(name='Ultra Laptop M2', description='...', price=38500, image='url', category_id=3)
        p4 = Product(name='4K Smart TV', description='...', price=19899, image='url', category_id=4)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        if not AboutPage.query.first():
            db.session.add(AboutPage(title='Hakkımızda', content='Elektronik mağazamız en yeni teknolojileri sunar.'))
            db.session.commit()

        if not ContactInfo.query.first():
            db.session.add(ContactInfo(name='Mağaza İletişim', email='info@elektronikmagaza.com', phone='0212 000 00 00', address='İstanbul, Türkiye'))
            db.session.commit()

# Bu kısım Flask 3.0'da before_first_request yerine kullanılır
with app.app_context():
    create_tables_and_seed()


# -----------------------------
# SAYFA ROTLARI
# -----------------------------

# Yönetici paneli rotaları
from flask import flash

@app.route('/admin', methods=['GET'])
def admin_panel():
    urunler = Product.query.all()
    kategoriler = Category.query.all()
    return render_template('admin.html', urunler=urunler, kategoriler=kategoriler)

@app.route('/admin/messages', methods=['GET'])
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

@app.route('/admin/urun-ekle', methods=['POST'])
def admin_urun_ekle():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image = request.form['image']
    category_id = request.form['category_id']
    urun = Product(name=name, description=description, price=price, image=image, category_id=category_id)
    db.session.add(urun)
    db.session.commit()
    flash('Ürün eklendi.')
    return redirect(url_for('admin_panel'))

@app.route('/admin/urun-sil', methods=['POST'])
def admin_urun_sil():
    urun_id = request.form['urun_id']
    urun = Product.query.get(urun_id)
    if urun:
        db.session.delete(urun)
        db.session.commit()
        flash('Ürün silindi.')
    return redirect(url_for('admin_panel'))

@app.route('/admin/urun-guncelle', methods=['POST'])
def admin_urun_guncelle():
    urun_id = request.form['urun_id']
    yeni_fiyat = request.form['price']
    urun = Product.query.get(urun_id)
    if urun and yeni_fiyat:
        urun.price = yeni_fiyat
        db.session.commit()
        flash('Ürün fiyatı güncellendi.')
    return redirect(url_for('admin_panel'))

@app.route('/hakkimizda')
def hakkimizda():
    about = AboutPage.query.first()
    return render_template('hakkimizda.html', about=about)

@app.route('/iletisim', methods=['GET', 'POST'])
def iletisim():
    contact = ContactInfo.query.first()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if name and email and message:
            db.session.add(ContactMessage(name=name, email=email, message=message))
            db.session.commit()
            return redirect(url_for('iletisim'))
    return render_template('iletisim.html', contact=contact)

Urun = namedtuple('Urun', ['id', 'ad', 'aciklama', 'fiyat', 'img'])
Kategori = namedtuple('Kategori', ['ad', 'img'])

# DB -> Template dönüştürücüleri (tasarımı korumak için)
def to_template_products(products):
    return [Urun(p.id, p.name, p.description or '', str(p.price), p.image or '') for p in products]

def to_template_categories(categories):
    return [Kategori(c.name, c.image or '') for c in categories]

def get_sepet():
    return session.get('sepet', [])

def set_sepet(sepet):
    session['sepet'] = sepet

@app.route('/')
def home():
    sepet_urun_sayisi = len(get_sepet())
    db_urunler = Product.query.all()
    db_kategoriler = Category.query.all()
    return render_template('home.html', urunler=to_template_products(db_urunler), kategoriler=to_template_categories(db_kategoriler), sepet_urun_sayisi=sepet_urun_sayisi)

@app.route('/sepet', methods=['GET', 'POST'])
def sepet():
    db_urunler = Product.query.filter(Product.id.in_(get_sepet())).all()
    sepet_urunler = to_template_products(db_urunler)
    # Fiyatları float'a çevirerek topla
    toplam_fiyat = sum(float(u.fiyat) for u in sepet_urunler)
    sepet_urun_sayisi = len(get_sepet())
    return render_template('sepet.html', sepet_urunler=sepet_urunler, toplam_fiyat=toplam_fiyat, sepet_urun_sayisi=sepet_urun_sayisi)

@app.route('/sepete-ekle', methods=['POST'])
def sepete_ekle():
    urun_id = int(request.form['urun_id'])
    sepet = get_sepet()
    if urun_id not in sepet:
        sepet.append(urun_id)
    set_sepet(sepet)
    return redirect(url_for('home'))

@app.route('/sepetten-sil', methods=['POST'])
def sepetten_sil():
    urun_id = int(request.form['urun_id'])
    sepet = get_sepet()
    if urun_id in sepet:
        sepet.remove(urun_id)
    set_sepet(sepet)
    return redirect(url_for('sepet'))

if __name__ == '__main__':
    app.run(debug=True)
