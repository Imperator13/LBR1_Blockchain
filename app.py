import datetime
import hashlib
import json
from flask import Flask, jsonify, render_template
import psycopg2
import pandas as pd


class Blockchain:
    def database_connect():
        connection = psycopg2.connect(database = 'tickets', user = 'darkskorpion', password = "darkskorpion", host = 'localhost', port = "5432")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM tickets")
        dataframe = cursor.fetchall()
        dataframe = pd.DataFrame(dataframe)
        print(dataframe)
        return dataframe


    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')


    def create_block(self, proof, previous_hash):
        dataframe = Blockchain.database_connect()
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'client_id': str(dataframe[0].iloc[len(self.chain)]),
                 'name': str(dataframe[1].iloc[len(self.chain)]),
                 'fan_id': str(dataframe[2].iloc[len(self.chain)]),
                 'ticket_number': str(dataframe[3].iloc[len(self.chain)]),
                 'purchase_time': str(dataframe[4].iloc[len(self.chain)]),
                 'email': str(dataframe[5].iloc[len(self.chain)]),
                 'phone_number': str(dataframe[6].iloc[len(self.chain)]),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
    

    def print_previous_block(self):
        return self.chain[-1]
    

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True
    

app = Flask(__name__)
blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'A block is MINED',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'client_id': block['client_id'],
                'name': block['name'],
                'fan_id': block['fan_id'],
                'ticket_number': block['ticket_number'],
                'purchase_time': block['purchase_time'],
                'email': block['email'],
                'phone_number': block['phone_number'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return render_template('mine_block.html', response = response), 200


@app.route('/display_chain', methods=['GET'])
def display_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return render_template('display_chain.html', response = response), 200


@app.route('/valid', methods = ['GET'])
def valid():
    valid = blockchain.chain_valid(blockchain.chain)
    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return render_template('valid.html', response = response), 200


@app.route('/')
def index():
    return render_template('index.html')


app.run(host='0.0.0.0')