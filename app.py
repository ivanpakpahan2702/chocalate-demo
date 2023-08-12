from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO,emit,send,join_room,leave_room
from datetime import datetime,timedelta

'''
import pytz
# Get the timezone object for New York
tz_NY = pytz.timezone('America/New_York') 
# Get the current time in New York
datetime_NY = datetime.now(tz_NY)
'''

now = datetime.now()
current_time = now.strftime("%D-%H:%M:%S")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_io = SocketIO(app, cors_allowed_origins="*",ping_interval=1,ping_timeout=10)

rooms = {}

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/',methods=['GET','POST'])
def auth():

    if request.method == "POST":
        username    = request.form.get("username")
        code_room   = str(request.form.get("code_room"))
        create      = request.form.get("create_room", False)
        join        = request.form.get("join_room", False)
    
        if create != False:
            if not username:
                return render_template("auth.html", error="Please enter a username.", code_room=code_room, username=username)
            elif not code_room:
                return render_template("auth.html", error="Please enter a code room.", code_room=code_room, username=username)
            elif len(code_room)<6:
                return render_template("auth.html", error="Code room must be in 6 digits.", code_room=code_room, username=username)
            elif (code_room) in rooms:
                return render_template("auth.html", error="Code room already exists.", code_room=code_room, username=username)
            else:
                room = code_room
                rooms[room] = {"members": 0,"users_username":[], "content": []}
                session["room"] = code_room
                session["username"] = username
                return redirect(url_for("room"))
        
        elif join != False:
            if not username:
                return render_template("auth.html", error="Please enter a username.", code_room=code_room, username=username)
            elif not code_room:
                return render_template("auth.html", error="Please enter a code room.", code_room=code_room, username=username)        
            elif code_room not in rooms:
                return render_template("auth.html", error="Room does not exist.", code_room=code_room, username=username)
            elif username in rooms[code_room]['users_username']:
                return render_template("auth.html", error="Username already exist.", code_room=code_room, username=username)
            else:
                session["room"] = code_room
                session["username"] = username
                return redirect(url_for("room"))
    
    return render_template('auth.html')


@app.route('/room',methods=['GET','POST'])
def room():
    room = session.get("room")
    if (room is None) or (session.get("username") is None) or (room not in rooms):
        return redirect(url_for("auth"))
    
    return render_template('room.html',code_room=room, messages=rooms[room]["content"],members=rooms[room]['members'])


@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for('auth'))

@socket_io.on('message')
def handle_message(message_file):
    room = session.get("room")
    if room not in rooms:
        return
    try:
        send(message_file, to=room)
        rooms[room]['content'].append(message_file)
    except:
        return

@socket_io.on('connect')
def connect(auth):
    room = session.get("room")
    username = session.get("username")
    join_room(room)
    rooms[room]['members'] += 1
    message_file = {'username': username, 'msg': " Connected!", 'time': current_time, 'members':rooms[room]['members']}
    socket_io.send(message_file, to=room);
    rooms[room]['content'].append(message_file)
    rooms[room]['users_username'].append(username)



@socket_io.on('disconnect')
def disconnect():
    room = session.get("room")
    username = session.get("username")
    rooms[room]['users_username'].remove(username)


    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        message_file = {'username': username, 'msg': None, 'time': current_time, 'members':rooms[room]['members']}
        socket_io.send(message_file, to=room);
        rooms[room]['content'].append(message_file)
        if rooms[room]["members"] <= 0:
            del rooms[room]


@socket_io.on_error() 
def error_handler(e):
    pass



if __name__ == '__main__':
    socket_io.run(app, debug=True)