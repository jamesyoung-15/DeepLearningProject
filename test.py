from collections import deque
q = deque(maxlen=5)

for  i in range(100000):
    q.append(i)

print(q)
print(sum(q))
print(max(q))