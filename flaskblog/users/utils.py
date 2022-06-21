import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


#fn = filename
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # An dieser Stelle wird das Bild runterskaliert (Es spart eine Menge Speicherplatz!)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''Um Ihr Passwort zurückzusetzen, folden Sie dem folgenden Link:
{url_for('users.reset_token', token=token, _external=True)} 
    
Wenn Sie ihr Passwort nicht zurücksetzen wollen, können Sie diese Email ignorieren
'''
    mail.send(msg)