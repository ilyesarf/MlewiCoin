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
		current_index = block['index']

		while current_index < len(chain):
			block = chain[current_index]
			previous_hash = self.hash(last_block)
			if block['previous_hash'] != previous_hash:
				return False

			if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
				return False

			last_block = block
			current_index += 1

		return True

	def resolve_problems(self):

		peers = self.nodes
		new_chain = None

		max_len = len(self.chain)

		for node in peers:
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				if length > max_len and self.valid_chain(chain):
					max_len = length
					new_chain = chain

		if new_chain:
			self.chain = new_chain
			return True

		return False

	def save_node(self, address):

		parsed_url = urlparse(address)
		if parsed_url.netloc:
			self.nodes.add(parsed_url.netloc)

		elif parsed_url.path:
			self.nodes.add(parsed_url.path)

		else:
			raise ValueError('Invalid URL')