import json
import random
from flask import Flask
from flask import request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, HiddenField, SubmitField, RadioField
from wtforms.validators import InputRequired, Email, Regexp
from helpfunctions import read_json
from helpfunctions import add_data_to_json

GOALS_DATA = read_json('goals.json')
WEEKDAYS_NAMES = read_json('weekdays.json')

app = Flask(__name__)
app.secret_key = 'my-key-what-was'
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
    clientPhone = db.Column(db.String(25))
    clientWeekday = db.Column(db.String(20))
    clientTime = db.Column(db.String(20))
    clientTeacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"))
    clientTeacher = db.relationship("Teacher", back_populates="bookings")


class Search(db.Model):
    """
    Таблица с заявками на подбор предподавателя
    """
    __tablename__ = "search"
    clientId = db.Column(db.Integer, primary_key=True)
    clientGoal = db.Column(db.String(20))
    clientTime = db.Column(db.String(25))
    clientName = db.Column(db.String(100))
    clientPhone = db.Column(db.String(20))

#инициализация Таблиц
db.create_all()


class BookinForm(FlaskForm):
    """
    Форма резервирования времени предподователя
    """
    clientWeekday = HiddenField('')
    clientTime = HiddenField('')
    clientTeacher = HiddenField('')
    clientName = StringField('Вас зовут', [InputRequired()])
    clientPhone = StringField('Ваш телефон', [InputRequired(), Regexp(regex=r'\+7 \d{3} \d{3} \d{4}', message='Телефон не соответсвует формату +7 XXX XXX XXXX')])
    submit = SubmitField('Записаться на пробный урок')


class SearchForm(FlaskForm):
    """
    Форма по подбору предподователя
    """
    clientTimeRadio = [
                       ("1-2", "1-2 часа в&nbsp;неделю"),
                       ("3-5", "3-5 часов в&nbsp;неделю"),
                       ("5-7", "5-7 часов в&nbsp;неделю"),
                       ("7-10", "7-10 часов в&nbsp;неделю")
                       ]
    clientGoal = RadioField('Какая цель занятий?',
                            choices=[(name, value['value']) for name, value in GOALS_DATA.items()])
    clientTime = RadioField('Сколько времени есть?', choices=clientTimeRadio)
    clientName = StringField('Вас зовут', [InputRequired()])
    clientPhone = StringField('Ваш телефон', [InputRequired(), Regexp(regex=r'\+7 \d{3} \d{3} \d{4}', message='Телефон не соответсвует формату +7 XXX XXX XXXX')])
    submit = SubmitField('Найдите мне преподавателя')


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
"""
#разовый Импорт
@app.route('/import/')
def export():
    import_db_from_teachersjson()
    db.session.commit()
    return 'Сохранено'
"""

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


@app.route('/booking/<id>/<day>/<time>', methods=['POST', 'GET'])
def booking(id, day, time):
    form = BookinForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            clientName = form.clientName.data
            clientPhone = form.clientPhone.data
            clientWeekday = form.clientWeekday.data
            clientTime = form.clientTime.data
            clientTeacher = db.session.query(Teacher).get((form.clientTeacher.data))
            #вот тут не понял как можно было бы использовать populate_obj в связанных
            booking_table = Booking(clientName=clientName, clientPhone=clientPhone, clientWeekday=clientWeekday,
                              clientTime=clientTime, clientTeacher=clientTeacher)
            db.session.add(booking_table)
            db.session.commit()

            return render_template('booking_done.html', clientName=clientName, clientTime=clientTime, clientPhone=clientPhone,
                                   clientWeekday=clientWeekday, weekdays=WEEKDAYS_NAMES)
    return render_template('booking.html', teacher=db.session.query(Teacher).get(id),
                            day=day, time=time, weekdays=WEEKDAYS_NAMES, form=form)


@app.route('/profile/<id>')
def profile(id):
    teacher = db.session.query(Teacher).get(id)
    teacher.free = eval(teacher.free)
    return render_template('profile.html', goals_data=GOALS_DATA,
                            teacher=teacher,
                            weekdays=WEEKDAYS_NAMES
                            )


@app.route('/search/', methods=['POST', 'GET'])
def search():
    form = SearchForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            clientGoal = form.clientGoal.data
            clientTime = form.clientTime.data
            clientName = form.clientName.data
            clientPhone = form.clientPhone.data
            search_table = Search()
            form.populate_obj(search_table)
            db.session.add(search_table)
            db.session.commit()
            return render_template('search_done.html', goal=GOALS_DATA[clientGoal],
                                    clientName=clientName, time=clientTime,
                                    clientPhone=clientPhone)
    return render_template('search.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
