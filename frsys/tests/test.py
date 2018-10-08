import time

print(int(round(time.time() * 1000))%10000000)
time.sleep(1)
print(int(round(time.time() * 1000))%10000000)