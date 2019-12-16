import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from time import sleep
import hashlib
import re

class Email:
	def __init__(self, sender):
		if sender != '':
			self.sender = sender
		else:
			self.sender = 'noreply@kek01.com'

	def buildPackage(self, path, receiver):
		self.msg = MIMEMultipart('alternative')
		self.msg['To'] = email.utils.formataddr(('', receiver))
		self.msg['From'] = email.utils.formataddr(('', self.sender))
		self.msg['Subject'] = 'E-mail accept'
		h = hashlib.sha256(bytes(receiver, encoding='utf-8')).hexdigest()
		try: 
			with open(path + "/" + path + ".html", "r") as file: html = file.read()
		except FileExistsError: print("Error. File doesn't exist")
		try: 
			with open(path + "/" + path + ".txt", "r") as file: text = file.read()
		except FileExistsError: print("Error. File doesn't exist")
		html = re.sub(r'<img src=',
			'<img src="http://kek01.pythonanywhere.com/link/auth/read/' + h + '"',
			html)
		html = re.sub(r'<a href=',
			'<a href="http://kek01.pythonanywhere.com/link/auth/confirm/' + h + '"',
			html)
		text += 'http://kek01.pythonanywhere.com/link/auth/confirm/' + h
		self.msg.attach(MIMEText(text, "plain"))
		self.msg.attach(MIMEText(html, "html")) 

	def sendPackage(self, path, receivers=['receiver_email@example.com']):
		try:
			with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
				server.login("login", "pass")
				for i in range(len(receivers)):
					self.buildPackage(path, receivers[i])
					server.sendmail(self.sender, receivers[i], self.msg.as_string())
					if i + 1 != len(receivers):
						sleep(7)
				print("Successfully sent email")
		except SMTPException: print("Error: unable to send email")