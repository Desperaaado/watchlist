from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Required

class MovieForm(FlaskForm):
    title = StringField('Title', validators=[Required(), Length(1,60)])
    year = StringField('Year', validators=[Required(), Length(1,4)])
    submit = SubmitField('Add')

class LoginForm(FlaskForm):
    user_name = StringField('User Name', validators=[Required(), Length(1, 20)])
    password = StringField('Password', validators=[Required(), Length(1, 60)])
    submit = SubmitField('Submit')
