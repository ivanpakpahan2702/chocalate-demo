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
socket_io = SocketIO(app, cors_allowed_origins="*")

rooms = {}

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/',methods=['GET','POST'])
def auth():
    global rooms
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
                rooms[room] = {"members": 0,"users_username":[username], "content": []}
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
                if username not in rooms[code_room]['users_username']:
                    rooms[code_room]['users_username'].append(username)
                return redirect(url_for("room"))
    
    return render_template('auth.html')


@app.route('/room',methods=['GET','POST'])
def room():
    global rooms
    room = session.get("room")
    if (room is None) or (session.get("username") is None) or (room not in rooms):
        return redirect(url_for("auth"))
    
    return render_template('room.html',code_room=room, messages=rooms[room]["content"],users_username=rooms[room]['users_username'])


@app.route('/logout',methods=['GET','POST'])
def logout():
    global rooms
    room = session.get("room")
    username = session.get("username")
    try:
        rooms[room]['users_username'].remove(username)  
    except:
        print('cannot delete username!')
    session.clear()
    return redirect(url_for('auth'))

@socket_io.on('message')
def handle_message(message_file):
    global rooms
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
    global rooms
    room = session.get("room")
    username = session.get("username")
    join_room(room)
    rooms[room]['members'] += 1
    if username not in rooms[room]['users_username']:
        try:
            rooms[room]['users_username'].append(username)
        except:
            print('cannot append username!')
    message_file = {'username': "Chocalate Server", 'msg': username+" has joined the room", 'time': current_time, 'users_username':rooms[room]['users_username']}
    socket_io.send(message_file, to=room);
    rooms[room]['content'].append(message_file)


@socket_io.on('client_disconnecting')
def disconnect(data):
    global rooms
    room = session.get("room")
    username = session.get("username")
    try:
        rooms[room]['users_username'].remove(username)  
    except:
        print('cannot delete username!')
    if room in rooms:
        rooms[room]["members"] -= 1
        message_file = {'username': 'Chocalate Server', 'msg': username+' has left the room', 'time': current_time, 'users_username':rooms[room]['users_username']}
        socket_io.send(message_file, to=room);
        leave_room(room)
        rooms[room]['content'].append(message_file)
        if rooms[room]["members"] <= 0:
            del rooms[room]
            return redirect(url_for('auth'))


@socket_io.on('client_now_typing')
def now_typing(data):
    message_file = {'username': data['username'], 'msg': data['msg'], 'time': current_time, 'users_username':rooms[room]['users_username'], 'status':'now typing'}
    print("==================================================TYPING==============================================")
    print(data)
    socket_io.send(message_file, to=room);


@socket_io.on('client_done_typing')
def done_typing(data):
    print("=====================================DONE TYPING===========================================================")
    print(data)
    message_file = {'username': data['username'], 'msg': data['msg'], 'time': current_time, 'users_username':rooms[room]['users_username'], 'status':'done typing'}
    socket_io.send(message_file, to=room);


@socket_io.on_error() 
def error_handler(e):
    pass



if __name__ == '__main__':
    socket_io.run(app, debug=True)