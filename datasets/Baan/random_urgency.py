from random import randint

# random 100 int number from 1 to 100
urgency = []
for _ in range(100):
    urgency.append(randint(1, 100))

# write into file
with open('urgency.txt', 'w') as fout:
    line = '\t'.join([str(x) for x in urgency]) + '\n'
    fout.write(line)
    fout.close()
