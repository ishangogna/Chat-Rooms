import os
from datetime import datetime
from flask import Flask,render_template,request,session,redirect,flash
from flask_socketio import SocketIO, emit,send
import collections
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

app.config["SECRET_KEY"] = "my secret key"
usersLogged = []
channelsCreated = []
channelMessages = dict()

@app.route("/")
def index():
    if "user" in session:
        if "channel" in session:
            return redirect("/channel/"+session["channel"])

        return render_template("index.html",user = session["user"],channelsCreated=channelsCreated)
    return render_template("login.html")


@app.route("/home")
def index2():
    return render_template("index.html",user = session["user"],channelsCreated=channelsCreated)

@app.route("/login", methods = ["POST","GET"])
def login():
    if request.method == "POST":
        user = request.form.get('user')
        if len(user) < 1 or user is '':
            return render_template('error.html',message = 'You need to provide a username')
        if user in usersLogged:
            return render_template('error.html',message = 'user already registered.')

        usersLogged.append(user)
        session['user'] = user
        session.permanent = True
        return redirect("/")
    else:
        return render_template('login.html')


@app.route("/logout",methods = ["GET"])
def logout():
    session.clear()
    flash('Successfully logged out')
    return redirect('/')
    


@app.route("/channel",methods = ["POST"])
def createChannel():
    channel = request.form.get("channel")
    if channel in channelsCreated:
        return render_template("error.html", message = "Channel already exists")
    else:
        channelsCreated.append(channel)
        channelMessages[channel] = collections.deque()
        return render_template('index.html',channelsCreated=channelsCreated,user = session["user"])


@app.route("/channel/<string:channelCreated>",methods = ["POST","GET"])
def channelView(channelCreated):
    session["channel"] = channelCreated
    if len(channelMessages[channelCreated])>10:
        channelMessages[channelCreated].popleft()
    print("from channel view " + str(channelMessages[channelCreated]))
    return render_template("view.html",channelCreated = channelCreated,channelMessages= channelMessages[channelCreated], user = session["user"])


@socketio.on('my event')
def handleEvent( json ):
    print('received something : ' + str(json))
    socketio.emit('my response',json)


@socketio.on('my message')
def handleMessage(json):
    string1 = str(json['data'])
    channel = str(json['data2'])
    timestamp = str(json['data3'])
    actualString = string1
    channelMessages[channel].append(actualString + "(" + timestamp + ")")
    print(channelMessages[channel])
    print(timestamp)
    
    print('received sometihng : ' + actualString)
    socketio.emit('my message response',{
        'user':session.get('user'),
        'message' : actualString,
        'timestamp' : timestamp,
    })

if __name__=="__main__":
    #socketio.run(app, debug = True)
    app.run()