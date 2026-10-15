from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, URLField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    has_sockets = BooleanField(label="Has Sockets")
    has_toilet = BooleanField(label="Has Toilets")
    has_wifi = BooleanField(label="Has Wifi")
    can_take_calls = BooleanField(label="Can Take Calls")
    submit = SubmitField(label='Submit')

class LoginForm(FlaskForm):
    username = StringField(label='Username:', validators=[DataRequired()], render_kw={'style':'font-family:var(--second-font)'})
    password = PasswordField('Password:', validators=[DataRequired()], render_kw={'style':'font-family:var(--second-font)'})
    submit = SubmitField(label='Submit', render_kw={'style':'font-family:var(--second-font)'})

class NewCafeForm(FlaskForm):
    name = StringField(label='Name:', validators=[DataRequired()])
    map_url = URLField(label='Map URL:', validators=[DataRequired()])
    img_url = URLField(label='Image URL:', validators=[DataRequired()])
    location = StringField(label='Location:', validators=[DataRequired()])
    has_sockets = BooleanField(label="Has Sockets")
    has_toilet = BooleanField(label="Has Toilets")
    has_wifi = BooleanField(label="Has Wifi")
    can_take_calls = BooleanField(label="Can Take Calls")
    seats = SelectField(label='Seats:', validators=[DataRequired()], choices = [
        ('0-10','0-10'), ('10-20','10-20'), ('20-30','20-30'), ('30-40','30-40'),
        ('40-50','40-50'), ('50+','50+')
    ])
    coffee_price = StringField(label='Coffee Price:', validators=[DataRequired()])
    submit = SubmitField(label='Submit')
    
    