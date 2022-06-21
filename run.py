from flaskblog import app, db
from flaskblog.models import User, Post


if __name__ == '__main__':
    app.run(debug=True)

#User.__table__.drop(db.engine)
#Post.__table__.drop(db.engine)

#db.create_all()