import json
import random
from flask import Flask
from flask import request
from flask import render_template


def find_teacher_id(id):
    for teacher in teachers:
        if teacher['id'] == int(id):
            return teacher


def create_json_from_data():
    import data
    with open('teachers.json', 'w') as f:
        json.dump(data.teachers, f, ensure_ascii=False)
    with open('goals.json', 'w') as f:
        json.dump(data.goals, f, ensure_ascii=False)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', teachers=random.sample(teachers, 6), goals=goals_data)


@app.route('/goals/<goal_id>/')
def goals(goal_id):
    if goal_id in goals_data:
        return render_template('goal.html', goal=goals_data[goal_id],
                                teachers=filter(lambda row: goal_id in row['goals'], teachers)
                                )
    else:
        return render_template('goal.html', goal="", teachers=teachers)

@app.route('/booking/<id>/<day>/<time>')
def booking(id, day, time):
    return render_template('booking.html', teacher=find_teacher_id(id),
                            day=day, time=time, weekdays=weekdays)


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
    return render_template('profile.html', goals_data=goals_data,
                            teacher=find_teacher_id(id),
                            weekdays=weekdays
                            )


@app.route('/search/')
def search():
    return render_template('search.html', goals=goals_data)


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


if __name__ == '__main__':
    with open('goals.json', 'r') as f:
        goals_data = json.load(f)
    with open('teachers.json', 'r') as f:
        teachers = json.load(f)
    with open('tabletime.json', 'r') as f:
        weekdays = json.load(f)
    app.run(host='0.0.0.0', port=8000, debug=True)
