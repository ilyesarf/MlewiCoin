from flask import Flask, jsonify, request
import json
import hashlib
from urllib.parse import urlparse
from time import time
from Crypto.PublicKey import RSA
import requests
import uuid4

app = Flask(__name__)
node_id = str(uuid4()).replace('-', '')


class Blockchain:
	def __init__(self):
		self.chain = []
		self.transactions = []
		self.nodes = set()

		self.new_block(previous_hash="1", proof=100)

	def new_block(self, proof, previous_hash=None):
		block = {
			'index': len(self.chain) + 1, 
			'timestamp': time(),
			'transactions': self.transactions,
			'proof': proof,
			'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}
		self.transactions = []
		self.chain.append(block)

		return block 

	def new_transaction(self, sender, receiver, amount): #Make New Transactions
		transaction = {
			'sender': sender,
			'receiver': receiver,
			'amount': amount,
		}
		self.transaction.append(transaction)
		return self.last_block

	def last_block(self):

		return self.chain[-1]

	def hash(self, block): #Hash_Function
		string_object = json.dumps(block, sort_keys=True)
		block_string = string_object.encode()

		hash = hashlib.sha256(block_string)
		hex_hash = hash.hexdigest()

		return hex_hash

	def valid_chain(self, chain): #Check if the chain is valid or not

		last_block  = chain[-1]
		current_index

