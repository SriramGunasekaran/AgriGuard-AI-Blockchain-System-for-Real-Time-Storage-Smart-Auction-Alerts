import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash="0", date="Genesis Block", predicted_price=0, actual_price=0)  

    def create_block(self, date, predicted_price, actual_price, previous_hash=None):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "date": date,
            "predicted_price": predicted_price,
            "actual_price": actual_price,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }
        self.chain.append(block)
        return block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def verify_chain(self):
        for i in range(1, len(self.chain)):
            if self.chain[i]["previous_hash"] != self.hash(self.chain[i - 1]):
                return False 
        return True
