from datetime import datetime, date
from sandwich import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    netto = db.Column(db.DECIMAL(), nullable=False, default=0)
    true_netto = db.Column(db.DECIMAL(), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', backref='user', lazy=True)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return "{}, {}, {}".format(self.username, self.email, self.netto)

    def calculate_wage(self, order_price=0):
        self.netto -= order_price
        
    def reset_wage(self):
        if self.last_login.month < datetime.today().month:
            self.netto = self.true_netto
            db.session.commit()

    def set_last_login(self):
        self.last_login = date.today()
        db.session.commit()


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    shop_of_the_day = db.Column(db.Boolean, default=False)
    sandwiches = db.relationship('Sandwich', backref='shop', lazy=True)

    def __repr__(self):
        return "{}, {}, Shop of the day: {}".format(self.name, self.email,
                                                    self.shop_of_the_day)


class Sandwich(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    price = db.Column(db.DECIMAL(), nullable=False)
    toppings = db.relationship('Topping', backref='sandwich', lazy=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)

    def __repr__(self):
        return "{}, {}".format(self.name, self.price)


class Topping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    price = db.Column(db.DECIMAL(), nullable=False)
    sandwich_id = db.Column(db.Integer, db.ForeignKey('sandwich.id'),
                            nullable=False)

    def __repr__(self):
        return "{}, {}".format(self.name, self.price)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.DECIMAL(), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "{}, {}, {}, {}, user_id: {}".format(self.name, self.price,
                                                    self.comment, self.date_posted, self.user_id)
