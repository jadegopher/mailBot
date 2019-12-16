from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, create_engine, Table, insert, update, select
from sqlalchemy.orm import Session
from socket import gethostname
import sshtunnel
import hashlib
import os
from re import split
from Email import Email
from User import User


host = gethostname()
port = 8080
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def getContacts(path):
	emails = []
	try:
		with open(path) as file:
			emails = split(r'\n', file.read())
		return emails
	except: print("something gone wrong")

def getFile():
	if 'emails' not in request.files:
		print('No file part')
	file = request.files['emails']
	filename = secure_filename(file.filename)
	try:
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return getContacts(UPLOAD_FOLDER + '/' + filename)
	except:
		return ''

def isUnique(session, dataBase, arg, receiver):
	users = session.execute('select * from ' + dataBase)
	for user in users:
		if user[arg] == receiver:
			return False
	return True

def write(data, tunnel):
	sqlAddr = 'mysql://login:pass@127.0.0.1:{}/login$table'.format(tunnel.local_bind_port)
	engine = create_engine(sqlAddr)
	session = Session(engine)
	metadata = MetaData(bind=engine)
	mytable = Table('user', metadata, autoload=True)
	for receiver in data:
		h = hashlib.sha256(bytes(receiver, encoding='utf-8')).hexdigest()
		if isUnique(session, 'user', 1, h):
			session.add(User(h, 0, False))
			session.commit()
	session.close()
	engine.dispose()

def read(tunnel):
	sqlAddr = 'mysql://login:pass@127.0.0.1:{}/login$table'.format(tunnel.local_bind_port)
	engine = create_engine(sqlAddr)
	session = Session(engine)
	metadata = MetaData(bind=engine)
	mytable = Table('user', metadata, autoload=True)
	users = session.execute('select * from user')
	user_list = []
	for user in users:
		user_list.append([])
		user_list[user[0] - 1].append(user[1])
		user_list[user[0] - 1].append(user[2])
		user_list[user[0] - 1].append(user[3])
	session.close()
	engine.dispose()
	return user_list

def setTunnel(data, typeCon):
	sshtunnel.SSH_TIMEOUT = 5.0
	sshtunnel.TUNNEL_TIMEOUT = 5.0
	with sshtunnel.SSHTunnelForwarder(
	('ssh.pythonanywhere.com'),
	ssh_username='login', ssh_password='pass',
	remote_bind_address=('kek01.mysql.pythonanywhere-services.com', 3306)
	) as tunnel:
		print("Tunnel set successfully!")
		if typeCon == 'write':
			write(data, tunnel)
		elif typeCon == 'read':
			return read(tunnel)
	print("Success!")

@app.route('/users')
def showTable():
	users = setTunnel(None, 'read')
	return render_template('list.html', users=users)

@app.route('/', methods=["GET", "POST"])
def root():
	if request.method == 'POST':
		if request.form['send_button'] == 'Send':
			receivers = getFile()
			if receivers == '' and request.form['receiver_email'] != '':
				receivers = []
				receivers.append(request.form['receiver_email'])
			elif receivers == '' and request.form['receiver_email'] == '':
				receivers = []
				receivers.append('receiver_email@example.com')
			print(receivers)
			setTunnel(receivers, 'write')
			em = Email(request.form['sender_email'])
			em.sendPackage('email', receivers)
		else: pass
	return render_template('menu.html')

if __name__ == '__main__':
	#postEmail(["test@example.ru", "test@example.com", "test@example.org"])
	app.run('localhost')
