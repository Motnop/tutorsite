import json
import random
from flask import Flask
from flask import request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from helpfunctions import read_json
from helpfunctions import add_data_to_json

GOALS_DATA = read_json('goals.json')
WEEKDAYS_NAMES = read_json('weekdays.json')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Teacher(db.Model):
    """
    Таблица предподавателей
    """
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    about = db.Column(db.String)
    rating = db.Column(db.Float)
    picture =db.Column(db.String)
    price = db.Column(db.Integer)
    goals = db.Column(db.String)
    free = db.Column(db.String)
    bookings = db.relationship("Booking", back_populates="clientTeacher")


class Booking(db.Model):
    """
    Таблица с зарезервированным временем у предподавателя
    """
    __tablename__ = "bookings"
    clientId = db.Column(db.Integer, primary_key=True)
    clientName = db.Column(db.String(100))
    clientPhone = db.Column(db.String(20))
    clientWeekday = db.Column(db.String(20))
    clientTime = db.Column(db.Time)
    clientTeacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    clientTeacher = db.relationship("Teacher", back_populates="bookings")


class Search(db.Model):
    """
    Таблица с заявками на подбор предподавателя
    """
    __tablename__ = "search"
    clientId = db.Column(db.Integer, primary_key=True)
    clientGoal = db.Column(db.String(20))
    clientTime = db.Column(db.Time)
    clientName = db.Column(db.String(100))
    clientPhone = db.Column(db.String(20))


db.create_all()

"""
#### Устаревшая функция по переносу данных их файла data.py
def create_json_from_data():
    import data
    with open('teachers.json', 'w') as f:
        json.dump(data.teachers, f, ensure_ascii=False)
    with open('goals.json', 'w') as f:
        json.dump(data.goals, f, ensure_ascii=False)
"""
"""
#### Одноразовая функция по переносу данных их json в DB
def import_db_from_teachersjson():

    teachers = read_json('teachers.json')
    for teacher in teachers:
        db.session.add(Teacher(name=teacher['name'], about=teacher['about'], rating=teacher['rating'],
                               picture=teacher['picture'], price=teacher['price'], goals=','.join(teacher['goals']),
                               free=str(teacher['free'])))
"""


@app.route('/import/')
def export():
    import_db_from_teachersjson()
    db.session.commit()
    return 'Сохранено'

#INDEX
@app.route('/')
def index():
    teachers = db.session.query(Teacher).all()
    return render_template('index.html', teachers=random.sample(teachers, 6), goals=GOALS_DATA)

#goal.html
@app.route('/goals/<goal_id>/')
def goals(goal_id):
    if goal_id in GOALS_DATA:
        teachers = db.session.query(Teacher).filter(Teacher.goals.contains(goal_id))
        return render_template('goal.html', goal=GOALS_DATA[goal_id],
                                teachers=teachers    #filter(lambda row: goal_id in row['goals'], teachers)
                                )
    else:
        teachers = db.session.query(Teacher).all()
        return render_template('goal.html', goal="", teachers=teachers)


@app.route('/booking/<id>/<day>/<time>')
def booking(id, day, time):
    return render_template('booking.html', teacher=db.session.query(Teacher).get(id),
                            day=day, time=time, weekdays=WEEKDAYS_NAMES)


@app.route('/booking_done/', methods=['POST'])
def booking_done():
    clientName = request.form['clientName']
    clientPhone = request.form['clientPhone']
    clientWeekday = request.form['clientWeekday']
    clientTime = request.form['clientTime']
    clientTeacher = request.form['clientTeacher']
    new_book = {
                "clientName": clientName,
                "clientPhone": clientPhone,
                "clientWeekday": clientWeekday,
                "clientTime": clientTime,
                "clientTeacher": clientTeacher
                }

    with open('booking.json', 'r') as f:
        json_bookings = json.load(f)
    json_bookings.append(new_book)
    with open('booking.json', 'w') as f:
        json.dump(json_bookings, f, ensure_ascii=False)
    return render_template('booking_done.html',
                           clientName=clientName,
                           clientTime=clientTime,
                           clientPhone=clientPhone,
                           clientWeekday=clientWeekday,
                           weekdays=weekdays
                           )


@app.route('/profile/<id>')
def profile(id):
    teacher = db.session.query(Teacher).get(id)
    teacher.free = eval(teacher.free)
    return render_template('profile.html', goals_data=GOALS_DATA,
                            teacher=teacher,
                            weekdays=WEEKDAYS_NAMES
                            )


@app.route('/search/')
def search():
    return render_template('search.html', goals=GOALS_DATA)


@app.route('/search_done/', methods=['POST'])
def search_done():
    form = request.form.get
    clientGoal = form('goal')
    clientTime = form('time')
    clientName = form('clientName')
    clientPhone = form('clientPhone')
    new_search = {
                  'clientGoal': clientGoal,
                  'clientTime': clientTime,
                  'clientName': clientName,
                  'clientPhone': clientPhone
                    }
    with open('search.json', 'r') as f:
        json_seach = json.load(f)
    json_seach.append(new_search)
    with open('search.json', 'w') as f:
        json_seach = json.dump(json_seach, f, ensure_ascii=False)

    return render_template('search_done.html', goal=goals_data[clientGoal],
                            clientName=clientName, time=clientTime,
                            clientPhone=clientPhone
                            )

print(db.session.query(Teacher).get(0))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
