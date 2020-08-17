from pwn import *
from constraint import *
import string


def find_answers(r1, r2, r3, r4):
    domain = string.ascii_letters + string.digits
    problem = Problem()
    problem.addVariables([f'v{i}' for i in range(1, 5)], domain)
    problem.addConstraint(lambda a, b: re.search(r1, a+b), ("v1", "v3"))
    problem.addConstraint(lambda a, b: re.search(r2, a+b), ("v2", "v4"))
    problem.addConstraint(lambda a, b: re.search(r3, a+b), ("v1", "v2"))
    problem.addConstraint(lambda a, b: re.search(r4, a+b), ("v3", "v4"))
    solutions = problem.getSolution()
    return solutions


def get_next(r):
    result = r.recv().decode('utf-8')
    print(result)
    result = result.replace('\u001b[32m', '')
    result = result.replace('\u001b[0m', '')
    lines = result.split()

    r1 = lines[0].strip()
    r2 = lines[1].strip().lstrip('|')
    r3 = lines[3].strip().rstrip('#')
    r4 = lines[7].strip().rstrip('#')

    print(r1, r2, r3, r4)

    answers = find_answers(r1, r2, r3, r4)

    print(answers)

    payload = " ".join(answers[f'v{i}'] for i in range(1, 5)) + '\n'
    print(payload)
    r.send(payload)
    sleep(0.1)
    for line in r.recvlines(5):
        print(line.decode('utf-8'))


r = remote('163.172.141.237', '1687')
for _ in range(5):
    r.recvuntil('________________________________________________')
r.recvline_regex('\s*\w+\s*')
sleep(0.1)
for _ in range(151):
    get_next(r)
