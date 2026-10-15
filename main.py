from forms import SearchForm, LoginForm, NewCafeForm
from flask import Flask, flash, render_template, redirect
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, ColumnElement, select
from werkzeug.security import check_password_hash
import random

# HINT: butter 




    

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'e3e9312c5e911e98604beb0fb6aa574600aef953deb16901bcce136a5b2b2571'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name='ck_cafe_has_sockets'), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name='ck_cafe_has_toilets'), nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name='ck_cafe_has_wifi'), nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name='ck_cafe_can_take_calls'), nullable=False)
    seats: Mapped[str] = mapped_column(String(50), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(50), nullable=True)

    def __init__(self, name, map_url, img_url, location, has_sockets, has_toilet, 
                 has_wifi, can_take_calls, seats, coffee_price):
        self.name = name
        self.map_url = map_url
        self.img_url = img_url
        self.location = location
        self.has_sockets = has_sockets
        self.has_toilet = has_toilet
        self.has_wifi = has_wifi
        self.can_take_calls = can_take_calls
        self.seats = seats
        self.coffee_price = coffee_price
    
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    
    def __init__(self, username, password):
            self.username = username
            self.password = password


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

@app.route("/hidden-login", methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if not login_form.validate_on_submit():
        return render_template('login.html', login_form=login_form)
    username, password = login_form.data['username'], login_form.data['password']
    requested_user = db.session.execute(select(User).where(User.username == username)).scalar()
    
    if requested_user is None:
        flash('User does not exist.')
        return render_template('login.html', login_form=login_form)
    
    if not check_password_hash(requested_user.password, password):
        flash('Incorrect password')
        return render_template('login.html', login_form=login_form)
    
    login_user(requested_user)
    return redirect('/search')

@app.route("/logout")
@login_required
def log_out():
    logout_user()
    return redirect('/')

@app.route("/")
def home_page():
    random_cafes = random.choices(db.session.execute(select(Cafe)).scalars().all(), k=3)
    return render_template('index.html', random_cafes=random_cafes)

@app.route("/search", methods = ['GET', 'POST'])
def search_cafes():
    search_form = SearchForm()
    
    result = db.session.execute(select(Cafe))
    cafes = result.scalars().all()
    
    if not search_form.validate_on_submit():
        return render_template('search.html', search_form=search_form, cafes=cafes)
    
    print(search_form.data)
    def return_conditions() -> list[ColumnElement[bool]]:
        conditions = []
        
        #Database only accepts integer booleans
        if search_form.data['has_sockets']:
            conditions.append(Cafe.has_sockets == int(search_form.data['has_sockets']))
        
        if search_form.data['has_toilet']:
            conditions.append(Cafe.has_toilet == int(search_form.data['has_toilet']))
        
        if search_form.data['has_wifi']:
            conditions.append(Cafe.has_wifi == int(search_form.data['has_wifi']))
        
        if search_form.data['can_take_calls']:
            conditions.append(Cafe.can_take_calls == int(search_form.data['can_take_calls']))       
        return conditions
        
    conditions = return_conditions()
    filtered_cafes = db.session.execute(select(Cafe).where(*conditions)).scalars().all()
    return render_template('search.html', search_form=search_form, cafes=filtered_cafes)

@app.route("/cafe/<int:cafe_id>")
def show_cafe(cafe_id):
    chosen_cafe = db.session.get(Cafe, cafe_id)
    return render_template('cafe.html', cafe=chosen_cafe)

@app.route("/new-cafe", methods=['GET','POST'])
@login_required
def create_cafe():
    create_form = NewCafeForm()
    if not create_form.validate_on_submit():
        return render_template('make_cafe.html', create_form=create_form)
    cafe_data = create_form.data
    
    new_cafe = Cafe(name = cafe_data['name'], map_url= cafe_data['map_url'], 
        img_url=cafe_data['img_url'], location = cafe_data['location'], 
        has_sockets= int(cafe_data['has_sockets']), has_toilet = int(cafe_data['has_toilet']), 
        has_wifi = int(cafe_data['has_wifi']), can_take_calls=int(cafe_data['can_take_calls']), 
        seats = cafe_data['seats'], coffee_price = cafe_data['coffee_price'])
    db.session.add(new_cafe)
    db.session.commit()
    return redirect('/search')

@app.route("/edit-cafe/<int:cafe_id>", methods=['GET','POST'])
@login_required
def edit_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    edit_form = NewCafeForm(
        name = cafe.name, map_url = cafe.map_url, img_url = cafe.img_url, location = cafe.location,
        has_sockets = cafe.has_sockets, has_toilet = cafe.has_toilet, has_wifi = cafe.has_wifi, 
        can_take_calls = cafe.can_take_calls, seats = cafe.seats, coffee_price=cafe.coffee_price
    )
    if not edit_form.validate_on_submit():
        return render_template('make_cafe.html', edit_form=edit_form, cafe_id=cafe_id)
    cafe_data = edit_form.data
    
    cafe.name = cafe_data['name']
    cafe.map_url = cafe_data['map_url']
    cafe.img_url = cafe_data['img_url']
    cafe.location = cafe_data['location']
    cafe.has_sockets = cafe_data['has_sockets']
    cafe.has_toilet = cafe_data['has_toilet']
    cafe.has_wifi = cafe_data['has_wifi']
    cafe.can_take_calls = cafe_data['can_take_calls']
    cafe.seats = cafe_data['seats']
    cafe.coffee_price = cafe_data['coffee_price']
    
    db.session.commit()
    return redirect('/search')

@app.route('/delete-cafe/<int:cafe_id>', methods=['GET'])
def delete_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe)
    db.session.commit()

    return redirect('/search')


if __name__ == '__main__':
    app.run(debug=True)