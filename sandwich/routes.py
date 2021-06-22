from datetime import date
from flask import url_for, render_template, redirect, request, abort
from sandwich import app, bcrypt, db, mail
from sandwich.forms import RegistrationForm, LoginForm, ShopForm, SandwichForm, OrderForm
from sandwich.models import User, Shop, Sandwich, Order
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import func

# TODO: flash messages
# TODO: Validation feedback

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('new_order'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            user.set_last_login()
            user.reset_wage()
            return redirect(next_page) if next_page else redirect(url_for('new_order'))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('new_order'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, true_netto=form.netto.data)
        user.netto = user.true_netto
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/admin')
@login_required
def index_shops():
    if current_user.is_admin is False:
        abort(403)
    fields = Shop.__table__.columns.keys()
    shops = Shop.query.all()
    return render_template('index_shops.html', title='Shops', fields=fields, shops=shops)


@app.route('/shop/new', methods=['GET', 'POST'])
@login_required
def new_shop():
    if current_user.is_admin is False:
        abort(403)
    form = ShopForm()
    if form.validate_on_submit():
        shop = Shop(name=form.name.data, email=form.email.data,
                    shop_of_the_day=form.shop_of_the_day.data)
        db.session.add(shop)
        db.session.commit()
        return redirect(url_for('index_shops'))
    return render_template('create_shop.html', title='New Shop', form=form, legend='Add A New Shop')


@app.route('/shop/<int:shop_id>/update', methods=['GET', 'POST'])
@login_required
def update_shop(shop_id):
    if current_user.is_admin is False:
        abort(403)
    shop = Shop.query.get_or_404(shop_id)
    form = ShopForm()
    if form.validate_on_submit():
        shop.name = form.name.data
        shop.email = form.email.data
        shop.shop_of_the_day = form.shop_of_the_day.data
        db.session.commit()
        return redirect(url_for('index_shops'))
    elif request.method == 'GET':
        form.name.data = shop.name
        form.email.data = shop.email
        form.shop_of_the_day.data = shop.shop_of_the_day
    return render_template('create_shop.html', title='Update Shop', form=form, legend='Update Shop')    


@app.route('/shop/<int:shop_id>/delete')
@login_required
def delete_shop(shop_id):
    if current_user.is_admin is False:
        abort(403)
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    return redirect(url_for('index_shops'))


@app.route('/sandwich/new', methods=['GET', 'POST'])
@login_required
def new_sandwich():
    if current_user.is_admin is False:
        abort(403)
    form = SandwichForm()
    form.shop.choices = [(shop.id, shop.name) for shop in Shop.query.group_by('name')]
    if form.validate_on_submit():
        shop = Shop.query.get(form.shop.data)
        sandwich = Sandwich(name=form.name.data, price=form.price.data, shop_id=form.shop.data)
        db.session.add(sandwich)
        db.session.commit()
        return redirect(url_for('new_sandwich'))
    return render_template('create_sandwich.html', title='New Sandwich', form=form)


@app.route('/order/new', methods=['GET', 'POST'])
@login_required
def new_order():
    form = OrderForm()
    try:
        shop = Shop.query.filter_by(shop_of_the_day=True).first()
        choices = shop.sandwiches
    except AttributeError:
        choices = []
    form.sandwich.choices = [(sandwich.id, sandwich.name) for sandwich in choices]
    if form.validate_on_submit():
        sandwich = Sandwich.query.get(form.sandwich.data)
        order = Order(name=sandwich.name, price=sandwich.price, comment=form.comment.data, user=current_user)
        current_user.calculate_wage(sandwich.price)
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('new_order'))
    if shop is None:
        return render_template('create_order.html', title='New Order', form=form, shop='No shop of the day selected')
    return render_template('create_order.html', title='New Order', form=form, shop=shop.name)


def send_order_mail(shop_of_the_day, orders):
    msg = Message('Bestelling van {}.'.format(date.today().strftime('%d/%m/%y')),
                  sender='noreply@intersentia.com',
                  recipients=[shop_of_the_day.email])
    msg.body = 'De bestelling: {}'.format(', '.join('broodje {} - aantal: {}'.format(*order) for order in orders))
    mail.send(msg)


@app.route('/order/send')
@login_required
def send_orders():
    if current_user.is_admin is False:
        abort(403)
    orders = Order.query.with_entities(Order.name, func.count(Order.name))\
                        .group_by(Order.name)\
                        .filter(Order.date_posted >= date.today()
                                .replace(day=1)).all()
    shop_of_the_day = Shop.query.filter_by(shop_of_the_day=True).first()
    send_order_mail(shop_of_the_day, orders)
    return redirect(url_for('index_shops'))

@app.route('/user/history')
@login_required
def show_history():
    orders = Order.query.filter_by(user_id=current_user.id)
    fields = Order.__table__.columns.keys()
    netto = round(current_user.netto, 2)
    return render_template('show_history.html', title='History', fields=fields, orders=orders, netto=netto)
