import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'rang_e_fatima_secret_key' # Flash messages aur sessions ke liye zaroori hai

# Database Configuration (Vercel ke liye /tmp folder aur local ke liye standard path)
if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/rang_e_fatima.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rang_e_fatima.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 1. Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    details = db.Column(db.String(500), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., 'home', '2pcs', '3pcs', etc.

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "details": self.details,
            "price": self.price,
            "tag": self.tag,
            "image": self.image
        }

# 2. Cart Model (Shopping Cart ke liye)
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    # Product relationship taake asani se product ki details mil sakein
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

# 3. Order Model (Checkout / Orders save karne ke liye)
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.String(50), nullable=False)

# Raw Products Data with Categories assigned for Database Seeding
PRODUCTS = [
    { "title": "Luxury Floral Print Raw Silk 3-Piece Suit", "details": "Includes Embroidered Neckline Shirt, Floral Wide Trousers & Organza Dupatta", "price": "PKR 18,500", "tag": "New Arrival", "image": "images/dress1.jpg.webp", "category": "home" },
    { "title": "Olive Green Embroidered Organza Luxury Formal", "details": "Intricate Thread & Sequins Work Shirt with Scalloped Organza Dupatta", "price": "PKR 24,500", "tag": "Luxury", "image": "images/dress2.jpg.webp", "category": "home" },
    { "title": "Lilac Chikankari Embroidered Cotton Lawn Suit", "details": "Schiffli Cutwork Shirt, Straight Trouser & Cutwork Organza Dupatta", "price": "PKR 12,900", "tag": "Bestseller", "image": "images/dress3.jpg.webp", "category": "home" },
    { "title": "Sky Blue Fine Embroidered Lawn 3-Piece Set", "details": "All-over Floral Thread Work Kurti with Lace Border Chiffon Dupatta", "price": "PKR 11,500", "tag": "Festive", "image": "images/dress4.jpg.webp", "category": "home" },
    { "title": "Gradient Blue Ombre Printed Lawn Suit", "details": "Soft Silk Dupatta with Embroidered Placket & Border Accents", "price": "PKR 9,800", "tag": "New", "image": "images/dress5.jpg.webp", "category": "home" },
    { "title": "Plum Magenta Gold Motif Printed 2-Piece Suit", "details": "Gold Paisley Print Long Kurti with Matching Trouser & Chiffon Dupatta", "price": "PKR 8,500", "tag": "Casual", "image": "images/dress6.jpg.webp", "category": "home" }
]

TWO_PIECE_PRODUCTS = [
    {"title": "Classic Digital Printed 2-Piece Suit", "details": "Printed Lawn Shirt with Matching Trouser", "price": "PKR 6,500", "tag": "2-Pc", "image": "images/dress7.jpg.webp", "category": "2pcs"},
    {"title": "Elegant Printed Cambric 2-Piece", "details": "Stylish Kurti with Dyed Trouser", "price": "PKR 6,900", "tag": "2-Pc", "image": "images/dress8.jpg.webp", "category": "2pcs"},
    {"title": "Floral Summer 2-Piece Pret", "details": "Printed Shirt & Cotton Pants", "price": "PKR 7,200", "tag": "2-Pc", "image": "images/dress9.jpg.webp", "category": "2pcs"},
    {"title": "Abstract Art Print 2-Piece Set", "details": "Modern Print Kurti with Straight Trousers", "price": "PKR 7,400", "tag": "2-Pc", "image": "images/dress10.jpg.webp", "category": "2pcs"},
    {"title": "Classic Printed Lawn 2-Piece Suit", "details": "Digital Printed Lawn Shirt with Matching Printed Trouser", "price": "PKR 6,850", "tag": "2-Pc Exclusive", "image": "images/dress11.jpg.webp", "category": "2pcs"},
    {"title": "Embroidered Motif Linen 2-Piece Set", "details": "Embroidered Neckline Kurti with Solid Straight Pants", "price": "PKR 7,500", "tag": "New Arrival", "image": "images/dress12.jpg.webp", "category": "2pcs"},
    {"title": "Chikankari Kurti with Tulip Trouser", "details": "Schiffli Cutwork Cotton Shirt Paired with Tulip Pants", "price": "PKR 8,200", "tag": "Bestseller", "image": "images/dress13.jpg.webp", "category": "2pcs"},
    {"title": "Pastel Printed Lawn Pret Set", "details": "Floral Print Long Kurti with Scalloped Edge Pants", "price": "PKR 6,950", "tag": "Casual Pret", "image": "images/dress14.jpg.webp", "category": "2pcs"},
    {"title": "Classic Printed 2-Piece Collection", "details": "Stylish Kurti and Matching Trouser", "price": "PKR 7,100", "tag": "2-Pc", "image": "images/dress15.jpg.webp", "category": "2pcs"},
    {"title": "Designer 2-Piece Formal Set", "details": "Printed Shirt with Dyed Trouser", "price": "PKR 7,800", "tag": "Trending", "image": "images/dress16.jpg.webp", "category": "2pcs"},
    {"title": "Mint Green 2-Piece Summer Suit", "details": "Lightweight Printed Kurti and Pants", "price": "PKR 6,700", "tag": "New", "image": "images/dress17.jpg.webp", "category": "2pcs"},
    {"title": "Royal Elegant 2-Piece Outfit", "details": "Matching Shirt & Trouser Combination", "price": "PKR 8,500", "tag": "Exclusive", "image": "images/dress18.jpg.webp", "category": "2pcs"},
    {"title": "Ready to Wear 2-Piece Kurti Set", "details": "Stitched Shirt with Straight Pants", "price": "PKR 5,900", "tag": "Pret", "image": "images/dress19.jpg.webp", "category": "2pcs"},
    {"title": "Casual Summer 2-Piece Attire", "details": "Daily Wear Printed Shirt and Trouser", "price": "PKR 6,200", "tag": "Casual", "image": "images/dress20.jpg.webp", "category": "2pcs"}
]

THREE_PIECE_PRODUCTS = [
    {"title": "Royal Velvet Embroidered 3-Piece Formal", "details": "Embroidered Velvet Shirt, Raw Silk Trousers & Heavy Organza Dupatta", "price": "PKR 22,500", "tag": "3-Pc Exclusive", "image": "images/dress21.jpg.webp", "category": "3pcs"},
    {"title": "Rose Pink Chikankari 3-Piece Suit", "details": "Schiffli Lawn Shirt, Cotton Pants & Cutwork Chiffon Dupatta", "price": "PKR 16,800", "tag": "New Arrival", "image": "images/dress22.jpg.webp", "category": "3pcs"},
    {"title": "Emerald Green Zardozi Festive Ensemble", "details": "Hand Embroidered Shirt, Wide Flare Trousers & Silk Dupatta", "price": "PKR 25,000", "tag": "Festive", "image": "images/dress23.jpg.webp", "category": "3pcs"},
    {"title": "Classic Embroidered Lawn 3-Piece", "details": "Detailed Neckline Shirt with Chiffon Dupatta & Trouser", "price": "PKR 12,500", "tag": "3-Pc", "image": "images/dress24.jpg.webp", "category": "3pcs"},
    {"title": "Sapphire Blue Printed 3-Piece Suit", "details": "Digital Printed Lawn Shirt, Trouser and Chiffon Dupatta", "price": "PKR 10,900", "tag": "Classic", "image": "images/dress25.jpg.webp", "category": "3pcs"},
    {"title": "Golden Sand Luxury Formal 3-Piece", "details": "Embroidered Organza Shirt with Raw Silk Trousers", "price": "PKR 19,800", "tag": "Luxury", "image": "images/dress26.jpg.webp", "category": "3pcs"},
    {"title": "Crimson Red Festive 3-Piece Ensemble", "details": "Heavy Thread Work Shirt with Jamawar Dupatta", "price": "PKR 21,000", "tag": "Festive", "image": "images/dress27.jpg.webp", "category": "3pcs"},
    {"title": "Lavender Bloom 3-Piece Lawn Suit", "details": "Pastel Printed Shirt, Dyed Trouser & Net Dupatta", "price": "PKR 11,200", "tag": "New", "image": "images/dress28.jpg.webp", "category": "3pcs"},
    {"title": "Teal Blue Chic 3-Piece Outfit", "details": "Modern Cutline Shirt with Embroidered Borders", "price": "PKR 13,500", "tag": "Trending", "image": "images/dress29.jpg.webp", "category": "3pcs"},
    {"title": "Peach Elegance Embroidered 3-Piece", "details": "Soft Tone Kurti with Matching Trousers & Dupatta", "price": "PKR 14,000", "tag": "Bestseller", "image": "images/dress30.jpg.webp", "category": "3pcs"},
    {"title": "Classic Ivory Formal 3-Piece Suit", "details": "Subtle Embroidery on Premium Fabric with Organza Dupatta", "price": "PKR 17,500", "tag": "Formal", "image": "images/dress31.jpg.webp", "category": "3pcs"}
]

LUXURY_PRODUCTS = [
    {"title": "Champagne Gold Heavily Embroidered Raw Silk Formal", "details": "Hand Crafted Dabka & Sequins Shirt, Wide Silk Pants & Tissue Dupatta", "price": "PKR 34,500", "tag": "Luxury Formal", "image": "images/dress32.jpg.jpg", "category": "luxury"},
    {"title": "Royal Velvet Masterpiece Luxury Suit", "details": "Intricate Zardozi Work Velvet Shirt with Jamawar Gharara", "price": "PKR 38,000", "tag": "Luxury", "image": "images/dress33.jpg.webp", "category": "luxury"},
    {"title": "Emerald Regal Luxury Formals", "details": "Hand-embroidered Organza Shirt with Raw Silk Trousers", "price": "PKR 36,500", "tag": "Exclusive", "image": "images/dress34.jpg.jpg", "category": "luxury"},
    {"title": "Crimson Garnet Festive Luxury Wear", "details": "Heavy Sequins & Pearl Embellished Shirt with Net Dupatta", "price": "PKR 29,500", "tag": "Luxury", "image": "images/dress35.jpg.webp", "category": "luxury"},
    {"title": "Midnight Blue Haute Couture Set", "details": "Signature Thread and Crystal Work Formal Ensemble", "price": "PKR 41,000", "tag": "Luxury", "image": "images/dress36.jpg.jpg", "category": "luxury"},
    {"title": "Blush Pink Pearled Luxury Attire", "details": "Delicate Handwork on Pure Organza with Silk Pants", "price": "PKR 31,000", "tag": "Luxury", "image": "images/dress37.jpg.jpg", "category": "luxury"},
    {"title": "Classic Ivory Signature Luxury Wear", "details": "Sophisticated Pearls and Cut-dana Embroidery", "price": "PKR 33,500", "tag": "Luxury", "image": "images/dress38.jpg.jpg", "category": "luxury"},
    {"title": "Ornate Plum Festive Luxury Suit", "details": "Rich Velvet Base with Gold Zari Embellishments", "price": "PKR 39,000", "tag": "Luxury", "image": "images/dress39.jpg.webp", "category": "luxury"},
    {"title": "Golden Heritage Luxury Ensemble", "details": "Traditional Motifs with Heavy Tissue Dupatta", "price": "PKR 35,000", "tag": "Luxury", "image": "images/dress40.jpg.jpg", "category": "luxury"},
    {"title": "Teal Sovereign Luxury Formal", "details": "Exquisite Hand Work on Premium Silk Fabric", "price": "PKR 37,500", "tag": "Luxury", "image": "images/dress41.jpg.jpg", "category": "luxury"},
    {"title": "Peach Glow Designer Luxury Suit", "details": "Subtle Pastels with Heavy Organza Detailing", "price": "PKR 28,500", "tag": "Luxury", "image": "images/dress42.jpg.jpg", "category": "luxury"},
    {"title": "Royal Maroon Velvet Luxury Edition", "details": "Bridal Inspired Cut with Heavy Embellished Borders", "price": "PKR 45,000", "tag": "Luxury", "image": "images/dress43.jpg.jpg", "category": "luxury"},
    {"title": "Silver Mint Luxury Formal Outfit", "details": "Contemporary Cut with Sparkling Sequins and Crystal Work", "price": "PKR 32,500", "tag": "Luxury", "image": "images/dress44.jpg.jpg", "category": "luxury"},
    {"title": "Embroidered Lawn Pret Luxury Suit", "details": "Ready-to-wear high-end luxury pret ensemble", "price": "PKR 14,500", "tag": "Luxury Pret", "image": "images/dress45.jpg.webp", "category": "luxury"},
    {"title": "Signature Designer Luxury Masterpiece", "details": "Fully Hand-Crafted Premium Formal Attire", "price": "PKR 48,000", "tag": "Luxury", "image": "images/dress46.jpg.webp", "category": "luxury"}
]

STITCHED_PRODUCTS = [
    {"title": "Ready-to-Wear Embroidered Kurti Pret", "details": "Stitched Designer Kurti with Embellishments", "price": "PKR 5,800", "tag": "Stitched", "image": "images/dress47.jpg.webp", "category": "stitched"},
    {"title": "Chic Stitched Lawn Pret Suit", "details": "Ready to wear shirt with matching trousers", "price": "PKR 7,500", "tag": "Stitched", "image": "images/dress48.jpg.webp", "category": "stitched"},
    {"title": "Embroidered Cotton Stitched Outfit", "details": "Ready-to-wear 2-piece stitched ensemble", "price": "PKR 8,200", "tag": "Stitched", "image": "images/dress49.jpg.webp", "category": "stitched"},
    {"title": "Printed Stitched Casual Kurti", "details": "Everyday wear stitched lawn shirt", "price": "PKR 4,900", "tag": "Stitched", "image": "images/dress50.jpg.webp", "category": "stitched"},
    {"title": "Festive Stitched 3-Piece Pret", "details": "Ready-to-wear embroidered shirt, trouser and dupatta", "price": "PKR 13,500", "tag": "Stitched", "image": "images/dress51.jpg.webp", "category": "stitched"},
    {"title": "Formal Stitched Luxury Pret", "details": "Embellished ready-to-wear formal attire", "price": "PKR 15,000", "tag": "Stitched", "image": "images/dress52.jpg.webp", "category": "stitched"},
    {"title": "Modern Cut Stitched Kurti", "details": "Stylish ready-to-wear casual top", "price": "PKR 5,200", "tag": "Stitched", "image": "images/dress53.jpg.webp", "category": "stitched"},
    {"title": "Elegant Stitched Lawn Suit", "details": "Stitched shirt and dyed trousers combo", "price": "PKR 7,900", "tag": "Stitched", "image": "images/dress54.jpg.webp", "category": "stitched"},
    {"title": "Classic Stitched Embroidered Pret", "details": "Ready to wear embroidered kurti with trousers and chiffon dupatta", "price": "PKR 14,500", "tag": "Stitched", "image": "images/dress55.jpg.webp", "category": "stitched"},
    {"title": "Sophisticated Stitched Formal Wear", "details": "Ready-to-wear party wear ensemble", "price": "PKR 16,200", "tag": "Stitched", "image": "images/dress56.jpg.webp", "category": "stitched"},
    {"title": "Designer Stitched Summer Pret", "details": "Trendy ready-to-wear outfit for everyday elegance", "price": "PKR 8,800", "tag": "Stitched", "image": "images/dress57.jpg.webp", "category": "stitched"}
]

UNSTITCHED_PRODUCTS = [
    {"title": "Classic Unstitched Lawn Suit", "details": "Unstitched Printed Shirt with Matching Lawn Dupatta & Trouser", "price": "PKR 4,800", "tag": "Unstitched", "image": "images/dress58.jpg.webp", "category": "unstitched"},
    {"title": "Embroidered Unstitched 3-Piece Collection", "details": "Unstitched Shirt with Neckline Embroidery and Voile Dupatta", "price": "PKR 7,500", "tag": "Unstitched", "image": "images/dress59.jpg.webp", "category": "unstitched"},
    {"title": "Summer Bloom Unstitched Fabric", "details": "Vibrant digital printed unstitched lawn outfit", "price": "PKR 5,200", "tag": "Unstitched", "image": "images/dress60.jpg.webp", "category": "unstitched"},
    {"title": "Royal Jacquard Unstitched Suit", "details": "Unstitched Jacquard Weaved Shirt with Dyed Trouser", "price": "PKR 8,900", "tag": "Unstitched", "image": "images/dress61.jpg.webp", "category": "unstitched"},
    {"title": "Chikankari Unstitched Lawn Material", "details": "Schiffli embroidered front with pure chiffon dupatta", "price": "PKR 9,500", "tag": "Unstitched", "image": "images/dress62.jpg.webp", "category": "unstitched"},
    {"title": "Pastel Hue Unstitched 3-Piece", "details": "Delicate floral prints on premium unstitched fabric", "price": "PKR 6,100", "tag": "Unstitched", "image": "images/dress63.jpg.webp", "category": "unstitched"},
    {"title": "Formal Unstitched Organza Ensemble", "details": "Heavy embroidered organza shirt panels with raw silk trouser", "price": "PKR 14,000", "tag": "Unstitched", "image": "images/dress64.jpg.webp", "category": "unstitched"},
    {"title": "Cambric Unstitched Winter/Fall Suit", "details": "Warm cambric unstitched fabric with rich prints", "price": "PKR 6,800", "tag": "Unstitched", "image": "images/dress65.jpg.webp", "category": "unstitched"},
    {"title": "Designer Unstitched Lawn Outfit", "details": "Exclusive unstitched dress material with embroidered border", "price": "PKR 7,900", "tag": "Unstitched", "image": "images/dress66.jpg.webp", "category": "unstitched"},
    {"title": "Elegance Unstitched Printed Set", "details": "Graceful everyday unstitched lawn combination", "price": "PKR 4,500", "tag": "Unstitched", "image": "images/dress67.jpg.webp", "category": "unstitched"},
    {"title": "Luxury Unstitched Festive Suit", "details": "Festive unstitched suit with zari work and net dupatta", "price": "PKR 11,500", "tag": "Unstitched", "image": "images/dress68.jpg.webp", "category": "unstitched"}
]

MEN_COTTON_PRODUCTS = [
    {"title": "Classic White Men Cotton Kameez Shalwar", "details": "Premium breathable summer cotton fabric with fine stitching", "price": "PKR 4,500", "tag": "Men Cotton", "image": "men/cotton1.jpg.webp", "category": "men-cotton"},
    {"title": "Charcoal Grey Designer Cotton Suit", "details": "Elegant executive wear cotton fabric for men", "price": "PKR 4,800", "tag": "Men Cotton", "image": "men/cotton2.jpg.webp", "category": "men-cotton"},
    {"title": "Navy Blue Executive Cotton Kurta Shalwar", "details": "Soft and durable premium cotton material", "price": "PKR 4,600", "tag": "Men Cotton", "image": "men/cotton3.jpg.webp", "category": "men-cotton"},
    {"title": "Beige Royal Men's Cotton Wear", "details": "Traditional textured cotton fabric with comfortable fit", "price": "PKR 4,900", "tag": "Men Cotton", "image": "men/cotton4.jpg.webp", "category": "men-cotton"},
    {"title": "Midnight Black Festive Cotton Suit", "details": "Rich dark tone pure cotton fabric for daily & formal wear", "price": "PKR 5,100", "tag": "Men Cotton", "image": "men/cotton5.jpg.webp", "category": "men-cotton"},
    {"title": "Olive Green Casual Men's Cotton Outfit", "details": "Lightweight breezy cotton fabric ideal for summer", "price": "PKR 4,400", "tag": "Men Cotton", "image": "men/cotton6.jpg.webp", "category": "men-cotton"}
]

MEN_WASHING_WEAR_PRODUCTS = [
    {"title": "Classic Executive Washing Wear Suit", "details": "Premium wrinkle-free fabric for all-day comfort", "price": "PKR 5,200", "tag": "Washing Wear", "image": "men/washing_wear1.jpg.webp", "category": "washing-wear"},
    {"title": "Royal Smooth Finish Washing Wear", "details": "Soft texture with elegant fall and premium feel", "price": "PKR 5,500", "tag": "Washing Wear", "image": "men/washing_wear2.jpg.webp", "category": "washing-wear"},
    {"title": "Modern Charcoal Washing Wear Kurta Shalwar", "details": "Durable and easy-care fabric for daily executive wear", "price": "PKR 4,900", "tag": "Washing Wear", "image": "men/washing_wear3.jpg.webp", "category": "washing-wear"},
    {"title": "Midnight Navy Soft Washing Wear", "details": "Breathable summer-friendly washing wear material", "price": "PKR 5,100", "tag": "Washing Wear", "image": "men/washing_wear4.jpg.webp", "category": "washing-wear"},
    {"title": "Pearl White Formal Washing Wear", "details": "Crisp and sophisticated look for formal occasions", "price": "PKR 5,800", "tag": "Washing Wear", "image": "men/washing_wear5.jpg.webp", "category": "washing-wear"},
    {"title": "Slate Grey Designer Washing Wear", "details": "Contemporary shade with fine texture and stitching ease", "price": "PKR 5,300", "tag": "Washing Wear", "image": "men/washing_wear6.jpg.webp", "category": "washing-wear"},
    {"title": "Classic Brown Festive Washing Wear", "details": "Rich traditional tone with premium finish", "price": "PKR 5,600", "tag": "Washing Wear", "image": "men/washing_wear7.jpg.jpg", "category": "washing-wear"}
]

# Helper function to auto-seed database on first launch
def seed_database():
    if Product.query.first() is None:
        all_data = (
            PRODUCTS + TWO_PIECE_PRODUCTS + THREE_PIECE_PRODUCTS + 
            LUXURY_PRODUCTS + STITCHED_PRODUCTS + UNSTITCHED_PRODUCTS + 
            MEN_COTTON_PRODUCTS + MEN_WASHING_WEAR_PRODUCTS
        )
        for item in all_data:
            p = Product(
                title=item['title'],
                details=item['details'],
                price=item['price'],
                tag=item['tag'],
                image=item['image'],
                category=item['category']
            )
            db.session.add(p)
        db.session.commit()
        print("Database seeded with initial products successfully!")

# Ensure database tables are created at startup for serverless (Vercel)
with app.app_context():
    db.create_all()
    seed_database()

# Routes
@app.route('/')
def home():
    products = Product.query.filter_by(category='home').all()
    return render_template('index.html', products=products)

@app.route('/2pcs')
def two_piece_page():
    products = Product.query.filter_by(category='2pcs').all()
    return render_template('twopiece.html', products=products)

@app.route('/3pcs')
def three_piece_page():
    products = Product.query.filter_by(category='3pcs').all()
    return render_template('threepiece.html', products=products)

@app.route('/luxury')
def luxury_page():
    products = Product.query.filter_by(category='luxury').all()
    return render_template('luxury.html', products=products)

@app.route('/stitched')
def stitched_page():
    products = Product.query.filter_by(category='stitched').all()
    return render_template('stitched.html', products=products)

@app.route('/unstitched')
def unstitched_page():
    products = Product.query.filter_by(category='unstitched').all()
    return render_template('unstitched.html', products=products)

@app.route('/men-cotton')
def men_cotton_page():
    products = Product.query.filter_by(category='men-cotton').all()
    return render_template('men_cotton.html', products=products)

@app.route('/washing-wear')
@app.route('/men-washing-wear')
def men_washing_wear_page():
    products = Product.query.filter_by(category='washing-wear').all()
    return render_template('men_washing_wear.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

# --- CART ROUTES ---
@app.route('/cart')
def view_cart():
    cart_items = CartItem.query.all()
    total_price = 0
    for item in cart_items:
        price_num = int(item.product.price.replace('PKR', '').replace(',', '').strip())
        total_price += price_num * item.quantity
    return render_template('cart.html', cart_items=cart_items, total_price=f"{total_price:,}")

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart_item = CartItem.query.filter_by(product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(product_id=product_id, quantity=1)
        db.session.add(cart_item)
        
    db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/remove-from-cart/<int:item_id>')
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    db.session.delete(cart_item)
    db.session.commit()
    return redirect(url_for('view_cart'))

# --- CHECKOUT ROUTES ---
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = CartItem.query.all()
    if not cart_items:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        
        total_price = 0
        for item in cart_items:
            price_num = int(item.product.price.replace('PKR', '').replace(',', '').strip())
            total_price += price_num * item.quantity
            
        new_order = Order(
            name=name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            total_amount=f"PKR {total_price:,}"
        )
        db.session.add(new_order)
        
        for item in cart_items:
            db.session.delete(item)
            
        db.session.commit()
        return render_template('order_success.html', order=new_order)
        
    return render_template('checkout.html')

@app.route('/search')
def search_products():
    query = request.args.get('q', '').strip()
    if query:
        results = Product.query.filter(
            (Product.title.ilike(f'%{query}%')) | 
            (Product.details.ilike(f'%{query}%')) | 
            (Product.tag.ilike(f'%{query}%'))
        ).all()
    else:
        results = []
    return render_template('search_results.html', query=query, products=results)

@app.route('/live-search')
def live_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    results = Product.query.filter(
        (Product.title.ilike(f'%{query}%')) | 
        (Product.details.ilike(f'%{query}%')) | 
        (Product.tag.ilike(f'%{query}%'))
    ).limit(6).all()
    
    return jsonify([p.to_dict() for p in results])

if __name__ == '__main__':
    app.run(debug=True)