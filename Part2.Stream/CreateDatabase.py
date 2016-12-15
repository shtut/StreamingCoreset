import csv
import random
import string
import os

class createDB:

    def __init__(self):
        g = open("1.csv", "wb")
        w = csv.writer(g)
        w.writerow(('id', 'name', 'address', 'college', 'company', 'dob', 'age'))
        for i in xrange(100000000):
            w.writerow((i + 1,
                        self.fake_name(random.choice(range(1, 10))),
                        self.fake_address(random.choice(range(5, 10))),
                        random.choice(['psg', 'sona', 'amirta', 'anna university']),
                        random.choice(['CTS', 'INFY', 'HTC']),
                        (random.randrange(1970, 2018, 1), random.randrange(1, 13, 1), random.randrange(1, 31, 1)),
                        random.choice(range(0, 100))))

    def fake_name(self, str_size):
        return ''.join(random.choice(string.ascii_letters) for _ in range(str_size))

    def fake_address(self, str_size):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(str_size))


createDB()