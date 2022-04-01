import hashlib
import rsa

class Block():
    def __init__(self,data,previous_hash,bob_pub,bob_priv):
        self.hash = hashlib.sha256()
        self.nonce = 0
        self.previous_hash = previous_hash
        self.bob_pub = bob_pub
        self.bob_priv = bob_priv
        self.data = rsa.encrypt((data).encode('utf8'), self.bob_pub)
    def __str__(self):
        return "{} {} {} {}".format(self.previous_hash.hexdigest(),self.hash,self.data,self.nonce)

    def mine(self,difficulty):
        self.hash.update(self.data)
        while int(self.hash.hexdigest() , 16) > 2**(256-difficulty):
            self.nonce += 1
            self.hash = hashlib.sha256()
            self.hash.update(str(self).encode('utf-8'))
        