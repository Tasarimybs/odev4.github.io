# Ana sayfa route'u eklendi (tanım dosyanın altına taşındı)
# -------------------------------------------------------
# IMPORTS
# -------------------------------------------------------
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash


# -------------------------------------------------------
# APP & DATABASE SETUP
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, instance_path=os.path.join(BASE_DIR, "instance"))
app.secret_key = "supersecret"

db_path = os.path.join(app.instance_path, "site.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------------------------------
# ADMIN AUTH CONFIG
# -----------------------------------------------
ALLOWED_ADMINS = {
    "caglar@gmail.com": "12345",
    "korhan@gmail.com": "12345",
    "cagber@gmail.com": "12345",
}

def _is_admin_path(path: str) -> bool:
    return path.startswith("/admin") and not path.startswith("/admin/giris")

@app.before_request
def _require_admin_login():
    if _is_admin_path(request.path):
        if not session.get("admin_logged"):
            next_url = request.url
            return redirect(url_for("admin_login", next=next_url))

@app.route("/admin/giris", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if ALLOWED_ADMINS.get(email) == password:
            session["admin_logged"] = True
            session["user_name"] = (email.split("@")[0].capitalize())
            next_url = request.args.get("next")
            return redirect(next_url or url_for("admin"))
        flash("Geçersiz e-posta veya şifre.")
        return render_template("admingiriş.html")
    if session.get("admin_logged"):
        return redirect(url_for("admin"))
    return render_template("admingiriş.html")

@app.route("/logout")
def logout():
    # If an admin session is present, send to admin login; otherwise go to home
    is_admin = session.get("admin_logged") is True
    session.clear()
    return redirect(url_for("admin_login")) if is_admin else redirect(url_for("home"))


@app.route("/logout-home")
def logout_home():
    # Her zaman ana sayfaya yönlendirerek çıkış yap
    session.clear()
    return redirect(url_for("home"))


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
    products = db.relationship("Product", backref="category", lazy=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))


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
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    address = db.Column(db.String(200))


campaign_products = db.Table(
    "campaign_products",
    db.Column("campaign_id", db.Integer, db.ForeignKey("campaign.id")),
    db.Column("product_id", db.Integer, db.ForeignKey("product.id"))
)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(400))
    image = db.Column(db.String(400))
    percent_discount = db.Column(db.Integer)
    min_cart_total = db.Column(db.Integer)
    starts_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)

    products = db.relationship(
        "Product",
        secondary=campaign_products,
        backref=db.backref("campaigns", lazy="dynamic")
    )


class FeaturedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    slot = db.Column(db.String(32))
    sort_order = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)


# -------------------------------------------------------
# SEPET HELPER
# -------------------------------------------------------
def get_sepet():
    return session.get("sepet", [])


def set_sepet(data):
    session["sepet"] = data


# -------------------------------------------------------
# HOME
@app.route("/")
def home():
    return render_template(
        "home.html",
        urunler=Product.query.all(),
        kategoriler=Category.query.all(),
        sepet_urun_sayisi=len(get_sepet())
    )


@app.route("/hakkimizda")
def hakkimizda():
    return render_template(
        "hakkimizda.html",
        about=AboutPage.query.first(),
        sepet_urun_sayisi=len(get_sepet())
    )

# -------------------------------------------------------
# PUBLIC PAGES
# -------------------------------------------------------
@app.route("/ara")
def ara():
    q = request.args.get("q", "")
    if q:
        urunler = Product.query.filter(
            (Product.name.ilike(f"%{q}%")) | (Product.description.ilike(f"%{q}%"))
        ).all()
    else:
        urunler = Product.query.all()
    return render_template(
        "home.html",
        urunler=urunler,
        kategoriler=Category.query.all(),
        sepet_urun_sayisi=len(get_sepet()),
        arama_sorgusu=q
    )


@app.route("/kampanyalar")
def kampanyalar():
    return render_template(
        "kampanyalar.html",
        kampanyalar=Campaign.query.filter_by(active=True).all(),
        sepet_urun_sayisi=len(get_sepet())
    )


@app.route("/iletisim", methods=["GET", "POST"])
def iletisim():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message_text = request.form.get("message")
        if name and email and message_text:
            msg = Message(name=name, email=email, message=message_text)
            db.session.add(msg)
            db.session.commit()
            flash("Mesajınız alındı", "success")
        else:
            flash("Lütfen tüm alanları doldurun", "error")
        return redirect(url_for("iletisim"))
    return render_template(
        "iletisim.html",
        sepet_urun_sayisi=len(get_sepet())
    )


def _build_sepet_urunler():
    sepet_raw = get_sepet() or []
    urunler = []
    normalized = []

    def _to_static_url(path_like: str):
        try:
            rel = str(path_like).lstrip("/")
            if rel.startswith("static/"):
                rel = rel[len("static/"):]
            return url_for("static", filename=rel)
        except Exception:
            return "https://via.placeholder.com/300x225?text=G%C3%B6rsel+Yok"

    for item in sepet_raw:
        pid = None
        adet = 1
        item_img = None
        if isinstance(item, int):
            pid = item
            adet = 1
        elif isinstance(item, dict):
            pid = item.get("id")
            adet = item.get("adet", 1)
            item_img = item.get("img")
        else:
            continue

        try:
            pid = int(pid)
        except (TypeError, ValueError):
            continue
        if not pid:
            continue

        p = Product.query.get(pid)
        if not p:
            continue

        raw_img = item_img or (p.image or None)
        if raw_img:
            if str(raw_img).startswith("http://") or str(raw_img).startswith("https://"):
                img_url = raw_img
            else:
                img_url = _to_static_url(raw_img)
        else:
            img_url = "https://via.placeholder.com/300x225?text=G%C3%B6rsel+Yok"

        urunler.append({
            "id": p.id,
            "name": (p.name or f"Ürün #{p.id}"),
            "description": (p.description or ""),
            "price": (p.price or 0),
            "image": img_url,
            "quantity": adet,
        })

        norm_entry = {"id": pid, "adet": adet}
        if raw_img:
            norm_entry["img"] = raw_img
        normalized.append(norm_entry)

    set_sepet(normalized)
    return urunler


@app.route("/sepet")
def sepet():
    sepet_urunler = _build_sepet_urunler()
    subtotal = sum((u.get("price", 0) or 0) * (u.get("quantity", 0) or 0) for u in sepet_urunler)
    applied_info = {}
    toplam_fiyat = subtotal
    # Basit kampanya indirimi: aktif yüzde indirimli ilk kampanyayı uygula
    active_campaign = Campaign.query.filter_by(active=True).order_by(Campaign.starts_at.desc()).first()
    if active_campaign and active_campaign.percent_discount:
        discount_amount = round(subtotal * (active_campaign.percent_discount / 100.0), 2)
        if discount_amount > 0:
            applied_info = {
                "campaign": active_campaign.title,
                "discount_amount": discount_amount,
            }
            toplam_fiyat = max(0, subtotal - discount_amount)
    # Benzer ürünler: sepetteki ürünlerle aynı kategoriden veya sepette olmayan son eklenen ürünlerden öneriler
    similar_products = []
    try:
        cart_ids = [u["id"] for u in sepet_urunler]
        # Try to infer first product's category
        first_pid = cart_ids[0] if cart_ids else None
        cat_id = None
        if first_pid:
            p0 = Product.query.get(first_pid)
            cat_id = p0.category_id if p0 else None
        query = Product.query
        if cat_id:
            query = query.filter(Product.category_id == cat_id)
        if cart_ids:
            query = query.filter(~Product.id.in_(cart_ids))
        # Fallback: if category filter yields none, lift category filter
        candidates = query.order_by(Product.id.desc()).limit(6).all()
        if not candidates:
            q2 = Product.query
            if cart_ids:
                q2 = q2.filter(~Product.id.in_(cart_ids))
            candidates = q2.order_by(Product.id.desc()).limit(6).all()
        for p in candidates:
            if p.image:
                if str(p.image).startswith("http://") or str(p.image).startswith("https://"):
                    img_url = p.image
                else:
                    try:
                        rel_path = str(p.image).lstrip("/")
                        if rel_path.startswith("static/"):
                            rel_path = rel_path[len("static/"):]
                        img_url = url_for('static', filename=rel_path)
                    except Exception:
                        img_url = "https://via.placeholder.com/300x225?text=G%C3%B6rsel+Yok"
            else:
                img_url = "https://via.placeholder.com/300x225?text=G%C3%B6rsel+Yok"
            similar_products.append({
                "id": p.id,
                "name": p.name or f"Ürün #{p.id}",
                "price": p.price,
                "image": img_url,
            })
    except Exception:
        similar_products = []
    return render_template(
        "sepet.html",
        sepet_urunler=sepet_urunler,
        subtotal=subtotal,
        toplam_fiyat=toplam_fiyat,
        applied_info=applied_info,
        similar_products=similar_products,
        sepet_urun_sayisi=len(get_sepet())
    )


@app.route("/sepete-ekle", methods=["POST"])
def sepete_ekle():
    urun_id = request.form.get("urun_id", type=int)
    p = Product.query.get(urun_id) if urun_id else None
    if not urun_id or not p:
        flash("Ürün bulunamadı", "error")
        return redirect(url_for("home"))
    sepet = get_sepet() or []
    found = False
    for idx, item in enumerate(sepet):
        if isinstance(item, int) and item == urun_id:
            sepet[idx] = {"id": urun_id, "adet": 2, "img": (p.image or None)}  # convert int to dict and increment
            found = True
            break
        elif isinstance(item, dict) and item.get("id") == urun_id:
            item["adet"] = item.get("adet", 1) + 1
            # ensure image is present
            if not item.get("img"):
                item["img"] = p.image or None
            found = True
            break
    if not found:
        sepet.append({"id": urun_id, "adet": 1, "img": (p.image or None)})
    set_sepet(sepet)
    flash("Ürün sepete eklendi", "success")
    # Eklemeden sonra geldiği sayfada kal (bildirim göster)
    return redirect(request.referrer or url_for("home"))


@app.route("/api/sepet-arttir", methods=["POST"])
def api_sepet_arttir():
    urun_id = request.form.get("urun_id", type=int)
    if not urun_id:
        return jsonify({"ok": False, "message": "Geçersiz ürün"}), 400
    p = Product.query.get(urun_id)
    if not p:
        return jsonify({"ok": False, "message": "Ürün bulunamadı"}), 404
    sepet = get_sepet() or []
    updated = False
    for item in sepet:
        if isinstance(item, dict) and item.get("id") == urun_id:
            item["adet"] = item.get("adet", 1) + 1
            if not item.get("img") and p.image:
                item["img"] = p.image
            updated = True
            break
        if isinstance(item, int) and item == urun_id:
            # Eski format: int → dict'e çevir ve 2 yap
            idx = sepet.index(item)
            sepet[idx] = {"id": urun_id, "adet": 2, "img": (p.image or None)}
            updated = True
            break
    if not updated:
        sepet.append({"id": urun_id, "adet": 1, "img": (p.image or None)})
    set_sepet(sepet)
    sepet_urunler = _build_sepet_urunler()
    subtotal = sum(u["fiyat"] * u["adet"] for u in sepet_urunler)
    return jsonify({
        "ok": True,
        "sepet_urun_sayisi": len(get_sepet()),
        "subtotal": subtotal,
    })


@app.route("/api/sepet-azalt", methods=["POST"])
def api_sepet_azalt():
    urun_id = request.form.get("urun_id", type=int)
    if not urun_id:
        return jsonify({"ok": False, "message": "Geçersiz ürün"}), 400
    sepet = get_sepet() or []
    for item in sepet:
        if isinstance(item, dict) and item.get("id") == urun_id:
            current = item.get("adet", 1)
            item["adet"] = max(1, current - 1)
            break
        if isinstance(item, int) and item == urun_id:
            # int ise 1 kabul edilir; azaltınca yine 1'de kalır
            break
    set_sepet(sepet)
    sepet_urunler = _build_sepet_urunler()
    subtotal = sum(u["fiyat"] * u["adet"] for u in sepet_urunler)
    return jsonify({
        "ok": True,
        "sepet_urun_sayisi": len(get_sepet()),
        "subtotal": subtotal,
    })


@app.route("/sepetten-sil", methods=["POST"])
def sepetten_sil():
    urun_id = request.form.get("urun_id", type=int)
    sepet_raw = get_sepet() or []
    sepet = []
    for i in sepet_raw:
        pid = i if isinstance(i, int) else (i.get("id") if isinstance(i, dict) else None)
        if pid is None or pid != urun_id:
            sepet.append(i if isinstance(i, dict) else {"id": i, "adet": 1})
    set_sepet(sepet)
    flash("Ürün sepetten kaldırıldı", "success")
    return redirect(url_for("sepet"))


@app.route("/urun/<int:urun_id>")
def urun_detay(urun_id):
    urun = Product.query.get_or_404(urun_id)
    return render_template(
        "urun_detay.html",
        urun=urun,
        sepet_urun_sayisi=len(get_sepet())
    )


@app.route("/profil")
def profil():
    user_id = session.get("user_id")
    if not user_id:
        flash("Lütfen giriş yapın", "error")
        return redirect(url_for("login"))
    user = User.query.get_or_404(user_id)
    return render_template(
        "profil.html",
        user=user,
        sepet_urun_sayisi=len(get_sepet())
    )


@app.route("/profil-guncelle", methods=["POST"])
def profil_guncelle():
    user_id = session.get("user_id")
    if not user_id:
        flash("Lütfen giriş yapın", "error")
        return redirect(url_for("login"))
    user = User.query.get_or_404(user_id)
    user.name = request.form.get("name", user.name)
    user.phone = request.form.get("phone", user.phone)
    user.address = request.form.get("address", user.address)
    db.session.commit()
    flash("Profil güncellendi", "success")
    return redirect(url_for("profil"))


# -------------------------------------------------------
# AUTH
# -------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            name=request.form["name"],
            email=request.form["email"]
        )
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()
        flash("Kayıt başarılı", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and user.check_password(request.form["password"]):
            session["user_id"] = user.id
            return redirect(url_for("home"))
        flash("Hatalı giriş", "error")
    return render_template("login.html")


# Removed duplicate logout; using single definition earlier that redirects to admin login


# -------------------------------------------------------
# ADMIN PANEL
# -------------------------------------------------------
@app.route("/admin")
def admin():
    return render_template(
        "admin.html",
        urunler=Product.query.all(),
        products=Product.query.all(),
        kategoriler=Category.query.all(),
        kampanyalar=Campaign.query.all(),
        about=AboutPage.query.first()
    )


@app.route("/admin/hakkimizda", methods=["GET"])
def admin_hakkimizda():
    about = AboutPage.query.first()
    return render_template("adminhakkimizda.html", about=about)


@app.route("/admin/hakkimizda-guncelle", methods=["POST"])
def admin_hakkimizda_guncelle():
    about = AboutPage.query.first()
    if not about:
        about = AboutPage(
            title=request.form["title"],
            content=request.form["content"]
        )
        db.session.add(about)
    else:
        about.title = request.form["title"]
        about.content = request.form["content"]

    db.session.commit()
    flash("Hakkımızda güncellendi", "success")
    return redirect(url_for("admin_hakkimizda"))
# -------------------------------------------------------
# ADMIN PROFILES
# -------------------------------------------------------
@app.route("/admin/profiller")
def admin_profiller():
    q = request.args.get("q", "")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (User.name.ilike(like)) |
            (User.email.ilike(like)) |
            (User.phone.ilike(like))
        )

    total_users = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    # Stats
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    new_users_this_month = User.query.filter(User.created_at >= start_of_month).count()

    # Pagination info
    total_pages = (total_users + per_page - 1) // per_page if per_page > 0 else 1
    start = (page - 1) * per_page + 1 if total_users > 0 else 0
    end = min(page * per_page, total_users)

    def _page_url(n):
        args = request.args.to_dict()
        args.update({"page": n, "per_page": per_page})
        return url_for("admin_profiller", **args)

    pages = [{"number": n, "url": _page_url(n), "active": (n == page)} for n in range(1, max(total_pages, 1) + 1)]
    pagination = {
        "total": total_users,
        "start": start,
        "end": end,
        "prev_url": _page_url(max(page - 1, 1)),
        "next_url": _page_url(min(page + 1, max(total_pages, 1))),
        "pages": pages,
    }

    return render_template(
        "admin_profiller.html",
        users=users,
        total_users=total_users,
        new_users_this_month=new_users_this_month,
        pagination=pagination,
    )


@app.route("/admin/profiller/export")
def admin_profiller_export():
    import csv
    from io import StringIO
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "name", "email", "phone", "address", "created_at"])
    for u in User.query.order_by(User.created_at.desc()).all():
        writer.writerow([
            u.id,
            u.name,
            u.email,
            u.phone or "",
            (u.address or "").replace("\n", " "),
            u.created_at.strftime('%Y-%m-%d %H:%M:%S') if u.created_at else ""
        ])
    csv_data = buf.getvalue()
    return Response(csv_data, mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=profiller.csv"
    })


# -------------------------------------------------------
# ADMIN MESSAGES
# -------------------------------------------------------
@app.route("/admin/mesajlar")
def admin_mesajlar():
    q = request.args.get("q", "")
    query = Message.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Message.name.ilike(like)) |
            (Message.email.ilike(like)) |
            (Message.message.ilike(like))
        )
    messages = query.order_by(Message.created_at.desc()).all()
    return render_template("adminmesaj.html", messages=messages)


@app.route("/admin/mesajlar/export")
def admin_mesajlar_export():
    import csv
    from io import StringIO
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "name", "email", "message", "created_at"])
    for m in Message.query.order_by(Message.created_at.desc()).all():
        writer.writerow([
            m.id,
            m.name,
            m.email,
            m.message.replace("\n", " ") if m.message else "",
            m.created_at.strftime('%Y-%m-%d %H:%M:%S') if m.created_at else ""
        ])
    csv_data = buf.getvalue()
    return Response(csv_data, mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=mesajlar.csv"
    })


# -------------------------------------------------------
# ADMIN FEATURED/VITRIN
# -------------------------------------------------------
@app.route("/admin/vitrin/ekle", methods=["POST"])
def admin_vitrin_ekle():
    try:
        product_id = request.form.get("product_id", type=int)
        category = (request.form.get("category") or "").strip()  # vitrinde kullanılacak slot/kategori
        sort_order = request.form.get("sort_order", type=int) or 1
        price = request.form.get("price", type=float)
        image = request.form.get("image")
        name = (request.form.get("name") or "").strip()

        if not product_id or not category:
            flash("Ürün ID ve kategori zorunludur.", "error")
            return redirect(url_for("admin"))

        # Kategori kodunu görsel isimlendirmeyle eşleştir
        def _category_display_name(code: str) -> str:
            mapping = {
                "telefonlar": "Telefonlar",
                "televizyonlar": "Televizyonlar",
                "bilgisayarlar": "Bilgisayarlar",
                "tabletler": "Tabletler",
                "kulakliklar": "Kulaklıklar",
            }
            return mapping.get((code or "").lower(), code.title())

        # Kategori var mı? Yoksa oluştur
        cat_name = _category_display_name(category)
        cat_obj = Category.query.filter_by(name=cat_name).first()
        if not cat_obj:
            cat_obj = Category(name=cat_name)
            db.session.add(cat_obj)
            db.session.flush()  # id almak için commit etmeden flush yeter

        p = Product.query.get(product_id)
        if not p:
            # Ürün yoksa oluştur
            p = Product(
                id=product_id,
                name=(name or f"urun {product_id}"),
                description="",
                price=int(round(price or 0)) if price is not None else 0,
                image=image or None,
                category_id=cat_obj.id,
            )
            db.session.add(p)
        else:
            # Ürün varsa opsiyonel güncellemeler
            if name:
                p.name = name
            if price is not None:
                try:
                    p.price = int(price)
                except Exception:
                    p.price = int(round(price or 0))
            if image:
                p.image = image
            if cat_obj and (p.category_id != cat_obj.id):
                p.category_id = cat_obj.id
            db.session.add(p)

        # Aynı product + slot varsa sırasını güncelle, yoksa ekle
        existing = FeaturedItem.query.filter_by(product_id=product_id, slot=category).first()
        if existing:
            existing.sort_order = sort_order
            db.session.add(existing)
        else:
            fi = FeaturedItem(product_id=product_id, slot=category, sort_order=sort_order)
            db.session.add(fi)

        db.session.commit()
        flash("Ürün vitrine eklendi.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Vitrine eklenirken bir hata oluştu.", "error")
    return redirect(url_for("admin"))


@app.route("/admin/vitrin/sil", methods=["POST"])
def admin_vitrin_sil():
    try:
        name = (request.form.get("product_name") or "").strip()
        product_id = request.form.get("product_id", type=int)  # geriye dönük destek
        p = None
        if name:
            p = Product.query.filter_by(name=name).first()
        elif product_id:
            p = Product.query.get(product_id)

        if not p:
            flash("Silinecek ürün bulunamadı.", "error")
            return redirect(url_for("admin"))

        FeaturedItem.query.filter_by(product_id=p.id).delete()
        db.session.delete(p)
        db.session.commit()
        flash("Ürün vitrinden ve listeden kaldırıldı.", "success")
    except Exception:
        db.session.rollback()
        flash("Vitrinden kaldırma sırasında hata oluştu.", "error")
    return redirect(url_for("admin"))


# -------------------------------------------------------
# ADMIN CAMPAIGNS
# -------------------------------------------------------
@app.route("/admin/kampanyalar", methods=["GET"])
def admin_kampanyalar():
    kategoriler = Category.query.all()
    return render_template("admin_kampanya_duzenle.html", kategoriler=kategoriler)


@app.route("/admin/kampanyalar/ekle", methods=["POST"])
def admin_kampanyalar_ekle():
    title = request.form.get("title", "").strip()
    subtitle = request.form.get("subtitle", "").strip()
    discount_type = request.form.get("discount_type")
    discount_value = request.form.get("discount_value", type=float)
    target_category = request.form.get("target_category")
    starts_at_str = request.form.get("starts_at")
    ends_at_str = request.form.get("ends_at")
    image = request.form.get("image")

    if not title:
        flash("Kampanya başlığı gerekli", "error")
        return redirect(url_for("admin_kampanyalar"))

    percent_discount = None
    if discount_type == "percentage" and discount_value is not None:
        try:
            percent_discount = int(discount_value)
        except (TypeError, ValueError):
            percent_discount = None

    # parse datetimes (YYYY-MM-DDTHH:MM)
    def _parse_dt(s):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%dT%H:%M")
        except ValueError:
            return None

    starts_at = _parse_dt(starts_at_str)
    ends_at = _parse_dt(ends_at_str)

    kamp = Campaign(
        title=title,
        subtitle=subtitle,
        image=image,
        percent_discount=percent_discount,
        starts_at=starts_at,
        ends_at=ends_at,
        active=True
    )
    db.session.add(kamp)
    db.session.commit()
    flash("Kampanya oluşturuldu", "success")
    return redirect(url_for("admin"))


# -------------------------------------------------------
# ADMIN CARTS
# -------------------------------------------------------
@app.route("/admin/sepetler")
def admin_sepetler():
    # Aggregate CartItem entries per user
    from collections import defaultdict
    agg = defaultdict(lambda: {"item_count": 0, "total_amount": 0.0, "last_update": None})

    items = CartItem.query.all()
    for ci in items:
        p = Product.query.get(ci.product_id)
        if not p:
            continue
        qty = ci.quantity or 1
        agg[ci.user_id]["item_count"] += qty
        agg[ci.user_id]["total_amount"] += (p.price or 0) * qty
        lu = ci.created_at
        if lu and (agg[ci.user_id]["last_update"] is None or lu > agg[ci.user_id]["last_update"]):
            agg[ci.user_id]["last_update"] = lu

    rows = []
    total_revenue = 0.0
    for user_id, data in agg.items():
        u = User.query.get(user_id) if user_id else None
        name = (u.name if u else f"Misafir #{user_id}") if user_id is not None else "Misafir"
        email = u.email if u else "-"
        last_update = data["last_update"]
        # Simple status based on recency
        if last_update is None:
            status = "Terk Edilmiş"
        else:
            delta = datetime.now() - last_update
            if delta <= timedelta(hours=2):
                status = "Aktif"
            elif delta <= timedelta(days=7):
                status = "Beklemede"
            else:
                status = "Terk Edilmiş"

        rows.append({
            "name": name,
            "email": email,
            "item_count": data["item_count"],
            "total_amount": data["total_amount"],
            "status": status,
            "last_update": last_update,
        })
        total_revenue += data["total_amount"]

    active_count = len(rows)
    avg_cart_total = (total_revenue / active_count) if active_count else 0.0

    summary = {
        "active_count": active_count,
        "potential_revenue": total_revenue,
        "avg_cart_total": avg_cart_total,
    }

    # Optional search by q (name or email)
    q = request.args.get("q", "").strip().lower()
    if q:
        rows = [r for r in rows if q in (r["name"] or "").lower() or q in (r["email"] or "").lower()]

    # Sort by last update desc
    rows.sort(key=lambda r: r["last_update"] or datetime.min, reverse=True)

    return render_template("admin_sepet.html", rows=rows, summary=summary)


@app.route("/admin/sepetler/export")
def admin_sepetler_export():
    import csv
    from io import StringIO
    # Build same aggregation as listing
    from collections import defaultdict
    agg = defaultdict(lambda: {"item_count": 0, "total_amount": 0.0, "last_update": None})
    items = CartItem.query.all()
    for ci in items:
        p = Product.query.get(ci.product_id)
        if not p:
            continue
        qty = ci.quantity or 1
        agg[ci.user_id]["item_count"] += qty
        agg[ci.user_id]["total_amount"] += (p.price or 0) * qty
        lu = ci.created_at
        if lu and (agg[ci.user_id]["last_update"] is None or lu > agg[ci.user_id]["last_update"]):
            agg[ci.user_id]["last_update"] = lu

    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["user_id", "name", "email", "item_count", "total_amount", "last_update", "status"])
    for user_id, data in agg.items():
        u = User.query.get(user_id) if user_id else None
        name = (u.name if u else f"Misafir #{user_id}") if user_id is not None else "Misafir"
        email = u.email if u else "-"
        last_update = data["last_update"]
        if last_update is None:
            status = "Terk Edilmiş"
        else:
            delta = datetime.now() - last_update
            if delta <= timedelta(hours=2):
                status = "Aktif"
            elif delta <= timedelta(days=7):
                status = "Beklemede"
            else:
                status = "Terk Edilmiş"
        writer.writerow([
            user_id,
            name,
            email,
            data["item_count"],
            f"{data['total_amount']:.2f}",
            last_update.strftime('%Y-%m-%d %H:%M:%S') if last_update else "",
            status,
        ])

    csv_data = buf.getvalue()
    return Response(csv_data, mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=sepetler.csv"
    })


# -------------------------------------------------------
# RUN
# -------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
