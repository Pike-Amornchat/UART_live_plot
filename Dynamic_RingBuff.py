class Dynamic_RingBuff:
    def __init__(self,length):
        self.length = length
        self.buffer = []

    def add(self,data):
        if len(self.buffer) == self.length:
            del self.buffer[0]
            self.buffer.append(data)
        else:
            self.buffer.append(data)

