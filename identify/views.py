import os
import datetime
from flask import Flask, request, render_template
from flask.ext.pymongo import PyMongo

from at import Messenger
from phonenumber import PhoneNumber


# Create our application
app = Flask(__name__)

# Specify the static folder
app.static_folder = os.path.abspath("static")

# Specify mongidb database
app.config['MONGODB_DBNAME'] = 'identify'

# Initiate the database
mongo = PyMongo(app, config_prefix='MONGODB')


# Identify commands
COMMAND = ['lost', 'found', 'update', 'edit',  'existing', 'pata', 'poteza', 'potea', 'hariri', 'iliyopo']

LOST = ['lost', 'potea', 'poteza']

FOUND = ['found', 'pata']

SWAHILI = ['pata', 'poteza', 'potea', 'badilisha', 'iliyopo']

# Message response dictionary
dictionary = dict(
	found='Hello, Id with number %s has not yet been repoted as lost we have saved this details for future references',
	lost='Hello, the id %s has been found by %s. For inquiries call Identity',	
	waiting='The id %s has not been found yet, you will receive a message when it gets found. For inquiries call  Identity',
	existing='The number %s has already been reported as lost by %s',
	pata='Kitambulisho chenye nambari %s hakija ripotiwa na mwenyewe maelezo haya yamehifandiwa kwenye kanzibati zetu',
	poteza='Kitambulisho chenye nambari %s kimepatikana na %s. Kwa maswali zaidi piga simu kwa nambari %s',
	potea='Kitambulisho chenye nambari %s kimepatikana na %s. Kwa maswali zaidi piga simu kwa nambari Identity',	
	ngojea='Tutakuarifu japo kitambulisho chenye nambari %s kitapatikana. Kwa maswali zaidi piga simu kwa nambari Identity',
	iliyopo='Kupotea kwa kitambulisho chenye nambari %s imesha ripotiwa na %s. Kwa maswali zaidi piga simu kwa nambari Identity'
	)


@app.route('/', methods=['GET', 'POST'])
def handle_request():
	""" Get the message text and calls the required function to handle the command requested by the message """
	if request.method == 'POST':
		pass
	elif request.method == 'GET':
		now = datetime.datetime.now()
		return render_template('form.html', id=3, date=now)


	text = request.form['text']
	sender = request.form['from']
	date = request.form['date']
	id_ = request.form['id']
	
	if not text:
		return "No request has been made"

	# Save message to the database
	handle_new_message(id_, sender, text, date)

	# Get the specific request from the text message
	response = interpreter(text)	
	
	if response:
		command, numbers = response			
	else:
		phone = sender
		message = "Invalid request"	
		send_message(phone, message)
		return 'Failed'	
	
	if command in LOST:	
		for number in numbers:
			phone, message = handle_search_command(number, sender, command)
			send_message(phone, message)

	elif command in FOUND:		
		for number in numbers:
			phone, message = handle_found_command(number, sender, command)	
			send_message(phone, message)		

	else:
		phone = sender
		message = "You supplied an invalid command, please use found or lost then the id number"
		send_message(phone, message)	
	return 'Success'


def interpreter(message):
	words = str(message).split(' ')	

	if len(words) < 1:
		return

	command = words[0]		
	if command not in COMMAND:		
		return 
	
	numbers = words[1:]
	return str(command), numbers


def handle_new_message(id_, sender, message, date):
	messages = mongo.db['inbox']
	messages.insert({'id': id_, 'sender': sender, 'message':message, 'date': date})


def humanize(phone):
	if '+254' in phone:
		return phone.replace('+254', '0')
	elif '254' in phone:
		return phone.replace('254', '0')
	elif phone[0] == '0':
		return phone


def handle_search_command(number, sender, command):
	number = str(number).upper()	
	response = mongo.db.found.find_one({'number': number, 'status': False})
	if not response:
		lost = mongo.db.lost.find_one({'number': number, 'status': False})	
		if lost:
			if lost['sender'] == sender:
				phone = sender
				if command in SWAHILI:
					message = 'Tume pata reporti yako, tutakuarifu kitambulisho kikipatikana'
				else:
					message = 'We have already received your report, we\'ll inform you when the id gets found'				
			else:
				phone = sender
				if command in SWAHILI:
					message = dictionary['ngojea'] % (number, humanize(lost['sender']))
				else:					
					message = dictionary['waiting'] % (number, humanize(lost['sender']))
				
		else:
			mongo.db.lost.insert({'number': number, 'sender': sender,  'status': False})
			phone = sender
			if command in SWAHILI:
				message = dictionary['ngojea'] % number
			else:				
				message = dictionary['waiting'] % number
	else:		
		mongo.db.found.update_one({'number': number, 'sender': sender}, {'$set': {'status': True}},  upsert=True)		
		mongo.db.lost.update_one({'number': number, 'sender': sender}, {'$set': {'status': True}}, upsert=True)		
		phone = sender
		print "The sender", response['sender']
		message = dictionary[command] % (number, humanize(response['sender']))

	return phone, message


def handle_found_command(number, sender, command):
	number = str(number).upper()	
	response = mongo.db.lost.find_one({'number': number, 'status': False})	

	if not response:
		found = mongo.db.found.find_one({'number': number, 'status': False})		
		if found:
			if found['sender'] == sender:			
				phone = sender
				if command in SWAHILI:				
					message = 'Tume pata reporti yako, tutamuarifu mwenye kitambulisho atakapo jitokeza'
				else:
					message = 'We have already received your report, we\'ll send your number to the owner'
			else:
				phone = found['sender']
				if command in SWAHILI:
					message = 'Kitambulisho chenye nambari %s kimesha patikana na %s' % (number, humanize(sender))
				else:
					message = 'Id with number %s has already been reported as found by %s' % (number, humanize(sender))
		else:
			mongo.db.found.insert({'number': number, 'sender': sender, 'status': False})
			phone = sender
			if command in SWAHILI:
				message = 'Kitambulisho chenye nambari %s hakijaripotiwa, tutamuarifu mwenye kitambulisho atakapo jitokeza' % number
			else:
				message = 'Id with number %s has not yet been repoted as lost, your number has been saved for later referrence' % number
	else:
		phone = response['sender']
		mongo.db.found.insert({'number': number, 'sender': sender, 'status': True})		
		mongo.db.lost.update_one({'number': number}, {'$set': {'status': True}}, upsert=True)		
		if humanize(sender) == response['sender']:
			message = 'Seems like you found your own Id, Please be carefull not to lose it again. Thank you for using our services'
		else:
			message = dictionary['lost'] % (number, humanize(sender))
	return phone, message


def send_message(phone, message):
	phn = PhoneNumber(phone)
	phone = phn.valid_numbers()
	if phone:
		today = datetime.datetime.now()
		messages = mongo.db['outbox']
		messages.insert({'sender': 'Identity', 'message':message, 'recipient': phone, 'date': today})
		protocol = Messenger(phone, message)
		sent, failed, amount = protocol.send_message()
		if sent:
			messages.update_one({'recipient': phone, 'message': message}, {'$set': {'status': True, 'amount': amount}})
		elif failed:
			messages.update_one({'recipient': phone, 'message': message}, {'$set': {'status': False, 'amount': 0}})
	else:
		print "Invalid phone number"



