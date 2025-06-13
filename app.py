from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from datetime import datetime, timedelta
import json

# Inisialisasi waktu saat ini
now = datetime.now()
current_time = now.strftime("%D-%H:%M:%S")

# Inisialisasi aplikasi Flask dan SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket_io = SocketIO(app, cors_allowed_origins="*")

# Dictionary untuk menyimpan data room
rooms = {}

@app.before_request
def make_session_permanent():
    # Membuat session tetap selama 10 menit
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)

@app.route('/', methods=['GET', 'POST'])
def auth():
    global rooms
    # Jika user sudah punya session room, langsung redirect ke room
    if session.get('room') is not None:
        room = session.get("room")
        print('Room sudah ada kamu boleh masuk')
        try:
            if rooms[room] > 0:
                return redirect(url_for("room"))
        except:
            session.clear()
            return render_template('auth.html')
    else:
        if request.method == "POST":
            username = request.form.get("username")
            code_room = str(request.form.get("code_room"))
            create = request.form.get("create_room", False)
            join = request.form.get("join_room", False)

            # Proses pembuatan room baru
            if create != False:
                if not username:
                    return render_template("auth.html", error="Please enter a username.", code_room=code_room, username=username)
                elif len(username) > 50:
                    return render_template("auth.html", error="Max username's character is 50.", code_room=code_room, username=username)
                elif ' ' in username:
                    return render_template("auth.html", error="Username cannot contain space character", code_room=code_room, username=username)
                elif not code_room:
                    return render_template("auth.html", error="Please enter a code room.", code_room=code_room, username=username)
                elif len(code_room) < 6 or len(code_room) > 6:
                    return render_template("auth.html", error="Code room must be in 6 digits.", code_room=code_room, username=username)
                elif code_room in rooms:
                    return render_template("auth.html", error="Code room already exists.", code_room=code_room, username=username)
                else:
                    room = code_room
                    rooms[room] = {"members": 0, "users_username": [username], "content": []}
                    session["room"] = code_room
                    session["username"] = username
                    return redirect(url_for("room"))

            # Proses join ke room yang sudah ada
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

@app.route('/room', methods=['GET', 'POST'])
def room():
    global rooms
    room = session.get("room")
    # Jika session tidak valid, redirect ke auth
    if (room is None) or (session.get("username") is None) or (room not in rooms):
        return redirect(url_for("auth"))
    return render_template('room.html', code_room=room, messages=rooms[room]["content"], users_username=rooms[room]['users_username'])

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global rooms
    room = session.get("room")
    username = session.get("username")
    # Hapus username dari room saat logout
    try:
        rooms[room]['users_username'].remove(username)
    except:
        print('cannot delete username!')
    session.clear()
    return redirect(url_for('auth'))

@socket_io.on('message')
def handle_message(message_file):
    global rooms
    # Format pesan sebelum dikirim
    message_file['msg'] = message_file['msg'].replace('\n', '<br/>')
    message_file['msg'] = message_file['msg'].replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
    room = session.get("room")
    if room not in rooms:
        return
    if rooms[room]["members"] <= 0:
        del rooms[room]
        return redirect(url_for('auth'))
    try:
        send(message_file, to=room)
        # Simpan pesan jika ada isinya
        if (message_file['msg'] != '') or message_file['msg'] != None:
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
    # Tambahkan username ke daftar user jika belum ada
    if username not in rooms[room]['users_username']:
        try:
            rooms[room]['users_username'].append(username)
        except:
            print('cannot append username!')
    # Kirim pesan join ke semua member room
    message_file = {'username': "Chocalate Server", 'msg': username + " has joined the room", 'time': current_time, 'users_username': rooms[room]['users_username']}
    socket_io.send(message_file, to=room)
    rooms[room]['content'].append(message_file)

@socket_io.on('client_disconnecting')
def disconnect(data):
    global rooms
    room = session.get("room")
    username = session.get("username")
    # Hapus user dari room saat disconnect
    try:
        rooms[room]['users_username'].remove(username)
    except:
        print('cannot delete username!')
    if room in rooms:
        rooms[room]["members"] -= 1
        message_file = {'username': 'Chocalate Server', 'msg': username + ' has left the room', 'time': current_time, 'users_username': rooms[room]['users_username']}
        socket_io.send(message_file, to=room)
        leave_room(room)
        rooms[room]['content'].append(message_file)
        # Hapus room jika tidak ada member
        if rooms[room]["members"] <= 0:
            pth_current_time = str(current_time).replace(':', '_').replace('/', '_')
            message_file_name = "message_history/" + pth_current_time + '_message_.txt'
            '''
            try:
                with open(message_file_name, 'w') as convert_file:
                    convert_file.write(json.dumps(rooms[room]))
            except Exception as e:
                print(e)
            '''
            del rooms[room]
            return redirect(url_for('auth'))

@socket_io.on('client_now_typing')
def now_typing(data):
    username = session.get('username')
    room = session.get("room")
    try:
        message_file = {'username': username, 'msg': '', 'time': current_time, 'users_username': rooms[room]['users_username'], 'status': 'now typing'}
        socket_io.send(message_file, to=room)
    except:
        print('Error!')


@socket_io.on('client_done_typing')
def done_typing(data):
    username = session.get('username')
    room = session.get("room")
    message_file = {'username': username, 'msg': '', 'time': current_time, 'users_username': rooms[room]['users_username'], 'status': 'done typing'}
    socket_io.send(message_file, to=room)


@socket_io.on_error()
def error_handler(e):
    pass

if __name__ == '__main__':
    socket_io.run(app, port=5000, debug=True)