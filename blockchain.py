from flask import Flask, jsonify, request
import json
import hashlib
from urllib.parse import urlparse
from time import time
import requests
from uuid import uuid4

app = Flask(__name__)
node_id = str(uuid4()).replace('-', '')


class Blockchain:
	def __init__(self):
		self.chain = []
		self.transactions = []
		self.nodes = set()
		self.nodes.add("http://127.0.0.1:81")
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

	
	def hash(self, block): #Hash_Function
		string_object = json.dumps(block, sort_keys=True)
		block_string = string_object.encode()

		hash = hashlib.sha256(block_string)
		hex_hash = hash.hexdigest()

		return hex_hash

	@property
	
	def last_block(self):
		return self.chain[-1]


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

	def get_nodes(self):
		for node in self.nodes:
			re = requests.post(f"{node}/serve_nodes")
			for n in re.text:
				if n not in self.nodes:
					nodes = []
					nodes.append(n)
					return nodes
				else:
					pass
    

	def proof_of_work(self, last_block):

		last_proof = last_block['proof']
		last_hash = self.hash(last_block)

		proof = 0

		while self.valid_proof(last_proof, proof, last_hash) is False:
			proof += 1

		return proof

	def valid_proof(last_proof, proof, last_hash):

		guess = f'{last_proof}{proof}{last_hash}'.encode()
		hash_guess = hashlib.sha256(guess).hexdigest()
		return hash_guess[:4] == "0000"


blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_id,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/register_nodes', methods=['POST'])
def register_nodes():

    nodes = blockchain.get_nodes()
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.save_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/serve_nodes', methods=['POST'])
def serve_nodes():
    for node in list(blockchain.nodes):
    	return node, 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_problems()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
