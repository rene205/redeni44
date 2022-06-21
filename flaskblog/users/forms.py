from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    firstname = StringField('Vorname', validators=[DataRequired()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    username = StringField('Benutzername',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Kennwort', validators=[DataRequired()])
    confirm_password = PasswordField('Kennwort bestätigen',
                                     validators=[DataRequired(), EqualTo('password')])
    country = StringField('Land', validators=[DataRequired()])
    state = StringField('Bundesland', validators=[DataRequired()])
    city = StringField('Stadt', validators=[DataRequired()])
    contact = StringField('Telefonnummer', validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    zipcode = StringField('Postleitzahl', validators=[DataRequired()])

    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Dieser Benutzername wird bereits verwendet. Bitte wählen Sie einen anderen Benutzernamen.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Diese Email wird bereits verwendet. Bitte wählen Sie eine andere Email.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Kennwort', validators=[DataRequired()])
    remember = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')


class UpdateAccountForm(FlaskForm):
    firstname = StringField('Vorname', validators=[DataRequired()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    username = StringField('Benutzername',
                        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                    validators=[DataRequired(), Email()])
    picture = FileField('Profilbild auswählen ', validators=[FileAllowed(['png','jpg'])]) 
    country = StringField('Land', validators=[DataRequired()])
    state = StringField('Bundesland', validators=[DataRequired()])
    city = StringField('Stadt', validators=[DataRequired()])
    contact = StringField('Telefonnummer', validators=[DataRequired()])
    address = StringField('Adresse', validators=[DataRequired()])
    zipcode = StringField('Postleitzahl', validators=[DataRequired()])
    submit = SubmitField('Aktualisieren')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Dieser Benutzername wird bereits verwendet. Bitte wählen Sie einen anderen Benutzernamen.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Diese Email wird bereits verwendet. Bitte wählen Sie eine andere Email.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Passwort zurücksetzen')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Es gibt kein Knoto mit dieser E-Mail-Adresse.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Kennwort', validators=[DataRequired()])
    confirm_password = PasswordField('Kennwort bestätigen',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Passwort zurücksetzen')