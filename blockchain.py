import hashlib, json, copy, time, random, time, requests
from loguru import logger
import bitcoinlib

DIFFICULTY = 4 # Quantidade de zeros (em hex) iniciais no hash valido.

class Blockchain(object):
    '''Classe utilizada para representar um blockchain privado baseado no protocolo Bitcoin.'''

    def __init__(self):
        self.chain = []
        self.memPool = []
        self.nodes = set() # Conjunto para armazenar os nós registrados.
        self.createGenesisBlock()

    def registerNode(self, address):
        '''Registra um novo nó no conjunto de nós.'''
        self.nodes.add(address)
        return self.nodes
    
    def getNodes(self):
        return self.nodes

    def createGenesisBlock(self):
        '''Cria, minera e retorna o bloco gênesis do blockchain. Chamado somente no construtor.'''
        genesis_block = self.createBlock()
        self.mineProofOfWork(self.prevBlock)
        return genesis_block

    def createBlock(self):
        '''Cria um novo bloco, inclui todas as transações pendentes e adiciona ao chain. O bloco ainda não tem nonce válido.'''
        block = {
            'index': len(self.chain),
            'timestamp': int(time.time()),
            'transactions': self.memPool,
            'merkleRoot': self.generateMerkleRoot(self.memPool),
            'nonce': 0,
            'previousHash': self.getBlockID(self.chain[-1]) if (len(self.chain)) else '0'*64
        }
        self.memPool = []
        self.chain.append(block)
        return block

    def mineProofOfWork(self, block):
        '''Retorna um nonce válido para o bloco passado como argumento.'''
        nonce = 0
        while self.isValidProof(block, nonce) is False:
            nonce += 1
        return nonce
    
    def chainValue(self, chain):
        '''Retorna o valor do blockchain passado como argumento.'''
        value = 0
        for block in chain:
            for tx in block['transactions']:
                value += tx['amount']
        return value
    
    def isValidChain(self, chain):
        '''
        Dado uma chain passada como parâmetro, faz toda a verificação no blockchain se cada uma dos blocos é válido:
         1. PoW válido
         2. Transações assinadas e válidas
         3. Merkle Root válido
         4. Hash do bloco anterior válido.
        Retorna True se válido, False caso contrário.
        '''
        for block in chain:
            
            i = block['index']
            previousBlock = chain[i-1] if i > 0 else chain[0]
            
            
            if not self.isValidProof(block, block['nonce']):
                logger.info(f'Block {i} has invalid nonce.')
                return False
            
            for tx in block['transactions']:
                logger.info(f'Verifying transaction {tx}.')
                if not Blockchain.isValidTransaction(tx):
                    logger.info(f'Block {i} has invalid signature.')
                    return False
            
            if block['merkleRoot'] != self.generateMerkleRoot(block['transactions']):
                logger.info(f'Block {i} has invalid merkleRoot.')
                return False
            
            if block['previousHash'] != self.getBlockID(previousBlock) and i != 0:
                logger.info(f'Block {i} has invalid PreviousHash.')
                return False
        return True

    def resolveConflicts(self):
        ''' Consulta todos os nós registrados, e verifica se algum outro nó tem um blockchain mais comprido e válido. Em caso positivo, substitui seu próprio chain '''
        for node in self.nodes:
            response = requests.get(node + '/chain')
            if response.status_code == 200:
                node_chain = response.json()
                if self.isValidChain(node_chain):
                    if self.chainValue(node_chain) > self.chainValue(self.chain):
                        self.chain = node_chain
                        return True
        return False


    @staticmethod
    def isValidProof(block, nonce):
        '''Retorna `True` caso o nonce passado como argumento seja válido para o block passado como argumento, `False` caso contrário.'''
        block['nonce'] = nonce
        return Blockchain.getBlockID(block)[:DIFFICULTY] == '0' * DIFFICULTY

    def createTransaction(self, sender, recipient, amount, timestamp, privWifKey):
        '''Cria, insere no mempool e retorna uma nova transação, assinada pela chave privada WIF do remetente.'''
        
        tx = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': timestamp
        }
 
        tx['signature'] = Blockchain.sign(privWifKey, json.dumps(tx, sort_keys=True))
        
        if Blockchain.isValidTransaction(tx):    
            self.memPool.append(tx)
            logger.info(f'Transaction index {len(self.memPool)} is valid.')
            return tx
        else:
            logger.info(f'Transaction {tx} is invalid.')
            return None

    @staticmethod
    def generateMerkleRoot(transactions):
        '''Retorna a Merkle Root de um conjunto de transações.'''
        if len(transactions) == 0:
            return '0'*64

        txHashes = [] 
        for tx in transactions:
            txHashes.append(Blockchain.generateHash(tx))

        return Blockchain._hashTxHashes(txHashes)

    @staticmethod
    def _hashTxHashes(txHashes):
        ''' Função auxiliar recursiva para cálculo do MerkleRoot.'''
        if len(txHashes) == 1: # Condição de parada.
            return txHashes[0]

        if len(txHashes)%2 != 0: # Confere se a quantidade de hashes é par.
            txHashes.append(txHashes[-1]) # Se não for, duplica o último hash.

        newTxHashes = []
        for i in range(0,len(txHashes),2):       
            newTxHashes.append(Blockchain.generateHash(txHashes[i] + txHashes[i+1]))
        
        return Blockchain._hashTxHashes(newTxHashes)

    @staticmethod
    def generateHash(data):
        '''Retorna a hash SHA256 dos dados passados como argumento.'''
        blkSerial = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(blkSerial).hexdigest()

    @staticmethod
    def getBlockID(block):
        '''Retorna o ID do bloco passado como argumento. O ID de um bloco é o hash do seu cabeçalho.'''
        blockCopy = copy.copy(block)
        blockCopy.pop("transactions", None)
        return Blockchain.generateHash(blockCopy)

    @property
    def prevBlock(self):
        '''Retorna o último bloco da chain.'''
        return self.chain[-1]

    @staticmethod
    def getWifCompressedPrivateKey(private_key=None):
        '''Retorna a chave privada no formato WIF-compressed da chave privada hex.'''
        if private_key is None:
            private_key = bitcoinlib.random_key()
        return bitcoinlib.encode_privkey(bitcoinlib.decode_privkey((private_key + '01'), 'hex'), 'wif')
        
    @staticmethod
    def getBitcoinAddressFromWifCompressed(wif_pkey):
        '''Retorna o endereço Bitcoin da chave privada WIF-compressed.'''
        return bitcoinlib.pubtoaddr(bitcoinlib.privkey_to_pubkey(wif_pkey))

    @staticmethod
    def sign(wifCompressedPrivKey, message):
        '''Retorna a assinatura digital da mensagem e a respectiva chave privada WIF-compressed.'''
        return bitcoinlib.ecdsa_sign(message, wifCompressedPrivKey)

    @staticmethod
    def verifySignature(address, signature, message):
        '''Verifica se a assinatura é correspondente a mensagem e o endereço BTC.
        Você pode verificar aqui também: https://tools.bitcoin.com/verify-message/'''
        return bitcoinlib.ecdsa_verify(message, signature, address)
    
    @staticmethod
    def isValidTransaction(tx):
        tx_copy = tx.copy()
        sender = tx_copy['sender']
        signature = tx_copy['signature']
        tx_copy.pop('signature', None)
        message = json.dumps(tx_copy, sort_keys=True)
        return Blockchain.verifySignature(sender, signature, message)

    def printChain(self):

        for block in reversed(self.chain) :

            if (block['index'] < len(self.chain)):
                print(32*' ', 'A', 39*' ')
                print(32*' ', '|', 39*' ')

            print(' __________________________________________________________________\n| {0:<0} |\
                \n ------------------------------------------------------------------\
                \n| Índice:         Timestamp:              Nonce:                   |\n| {1:<16d}{2:<24d}{3:<25d}|\
                \n|                                                                  |\
                \n| Merkle Root:                                                     |\n| {4:<0} |\
                \n|                                                                  |\
                \n| Transações:                                                      |\n| {5:<16d}                                                 |\
                \n|                                                                  |\
                \n| Hash do último bloco:                                            |\n| {6:<0} |\
                \n ------------------------------------------------------------------'\
                .format(Blockchain.getBlockID(block),block['index'],block['timestamp'],block['nonce'],block['merkleRoot'],len(block['transactions']),block['previousHash']))



# Implemente sua API com os end-points indicados no GitHub Classroom.
# Implemente um teste com ao menos 2 nós simultaneos.

