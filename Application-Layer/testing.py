from Modules import *

buf = Dynamic_RingBuff(6)
buf.add(10)
start = time.time()
print('hi')
end = time.time()
print(end-start)