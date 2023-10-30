from flask import Flask, jsonify, request
from loguru import logger
from blockchain import Blockchain
import requests, json, time, argparse

app = Flask(__name__)
bc = Blockchain()

@app.route('/transactions/create', methods=['POST'])
def createTransaction():
    """Create a new transaction and add it to the mempool"""
    
    tx_data = request.get_json()
    required_fields = ['sender', 'recipient', 'amount', 'privWifKey']
    
    for field in required_fields:
        if not tx_data.get(field):
            return 'Missing data information.', 406
    
    timestamp = int(time.time())

    tx = bc.createTransaction(tx_data['sender'], tx_data['recipient'], tx_data['amount'], timestamp, tx_data['privWifKey'])
    
    if tx == None:
        return "Transaction is invalid.", 406
    return "Transaction is processing.", 200

@app.route('/chain', methods=['GET'])
def get_chain():
    """Response all the blocks in the chain at the moment"""
    
    bc.printChain()
    response = bc.chain
    return jsonify(response), 200

@app.route('/transactions/mempool', methods=['GET'])
def get_mempool():
    """Response all the transactions in the mempool at the moment"""
    
    mempool = bc.memPool
    return jsonify(mempool), 200

@app.route('/mine', methods=['GET'])
def mine():
    """Mine a new block and add it to the chain"""
    
    block = bc.createBlock()
    nonce = bc.mineProofOfWork(block)
    block['nonce'] = nonce
    return block

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """"""
    node_request = request.get_json()
    nodes = node_request['nodes']
    
    if nodes is None:
        return "Error: Node list are empty.", 400
    
    for node in nodes:
        bc.registerNode(node)
        
    return "Nodes registered", 200

@app.route('/nodes/resolve', methods=['GET'])
def nodes_resolve():
    if bc.resolveConflicts():
        return "Blockchain updated.", 200
    else:
        return "Blockchains larger and valid not found", 200

def create_app_instance(port):
    app.run(port=port, debug=True)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run multiple instances of the Flask app on different ports')
    parser.add_argument('--port', type=int, default=5001, help='Port number for the app instance')
    args = parser.parse_args()
    create_app_instance(args.port)

