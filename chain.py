import hashlib
from block import Block
import sqlite3
import rsa
import sqlite3
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

list_of_pubs = []
PKEY = rsa.PublicKey(8674147535994576382750065200599377986737727269397338793346972543034600735580991114663903452508384589290438289185100032794459866337346524596784499127944103, 65537)
list_of_pubs.append(PKEY)
counter = 0
class Chain():
    def __init__(self, difficulty,bob_pub,bob_priv):
        self.difficulty = difficulty
        self.blocks = []
        self.pool = []
        self.bob_pub = bob_pub
        self.bob_priv = bob_priv
        self.create_origin_block()

    def proof_of_work(self, block):
        hash = hashlib.sha256()
        hash.update(str(block).encode('utf-8'))
        return block.hash.hexdigest() == hash.hexdigest() and int(hash.hexdigest(), 16) < 2**(256-self.difficulty) and block.previous_hash == self.blocks[-1].hash
        
    def add_to_chain(self, block):
        if self.proof_of_work(block):
            self.blocks.append(block)
            
    def add_to_pool(self, data):
        #socket
        self.pool.append(data)
        
    def create_origin_block(self):
        h = hashlib.sha256()
        h.update('0'.encode('utf-8'))
        origin = Block("Origin", h,list_of_pubs[-1],list_of_pubs[-1])
        origin.mine(self.difficulty)
        self.blocks.append(origin)

    def add_to_DB(self,text,p_key , m_key):
        global counter
        conn = sqlite3.connect('mini_pro.db')
        cur = conn.cursor()
        p_key , m_key = rsa.newkeys(512)
        counter = counter + 1
        with open('keys/{}/pubkey.pem'.format(counter), mode='wb') as f:
            f.write(p_key.save_pkcs1('PEM'))
        with open('keys/{}/privkey.pem'.format(counter), mode='wb') as f:
            f.write(m_key.save_pkcs1('PEM'))
        cur.execute("UPDATE voter_info SET vote_status = 1 WHERE voter_id = ?",(int(text),))
        conn.commit()
        #str(rsa.encrypt(self.blocks[-1].data.encode('utf8'),list_of_pubs[-1]))
        cur.execute("INSERT INTO remote_ledger_copy VALUES(?,?,?,?)",(str(self.blocks[-1].previous_hash.hexdigest()),(str(self.blocks[-1].hash.hexdigest())),str(p_key),self.blocks[-1].data))
        cur.execute("SELECT * FROM remote_ledger_copy")
        daaaata = cur.fetchall()
        list_of_pubs.append(p_key)
        conn.commit()
        
    def mine(self,p_key , m_key):
        print("I am mining")
        if len(self.pool) > 0:

            data = self.pool.pop()
            block = Block(data, self.blocks[-1].hash,list_of_pubs[-1],list_of_pubs[-1])
            block.mine(self.difficulty)
            self.add_to_chain(block)
            print("Previous Hash: ",block.previous_hash.hexdigest())
            print("Hash: ",block.hash.hexdigest())
            print("Data: ",block.data)
            #print("Data: ",data)
            print("========== ========")