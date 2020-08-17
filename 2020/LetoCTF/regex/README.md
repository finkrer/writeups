# Regex

Подключаемся по nc к нужному порту и видим примерно такую картину:

```
        [jgTv]+  |[gce9]+
        #################
Fn|PA|v9#       #       #
        #################
[^WD6t]+#       #       #
        #################
```

Кажется, нас просят пройти капчу, чтобы доказать, что мы робот.

Из описания понимаем суть задания: нужно поместить в ячейки такие буквы,
чтобы слово, получающееся в каждом столбце и строке, соответствовало регулярке.

Видимо, для начала нам придется получить сами регулярки.

Для взаимодействия с сервисом используем [pwntools](http://docs.pwntools.com/en/stable/).

Подключаемся, пропускаем вступление и начинаем работать с заданиями.

```python
r = remote('163.172.141.237', '1687')
for _ in range(5):
    r.recvuntil('________________________________________________')
r.recvline_regex('\s*\w+\s*')
sleep(0.1)
for _ in range(151):
    get_next(r)
```

Убираем ANSI-последовательности цветов из ответа, разбиваем на строки и методом тыка находим,
какие из них соответствуют регуляркам.

```python
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
```

Теперь подумаем над самим заданием.

Чем-то напоминает судоку, не так ли? Вспоминаем (или не вспоминаем), что такие задачи как-то называются.

Путем гуглинга устанавливаем, что это [Constraint Satisfaction Problem](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem). Читаем и выясняем, что для таких задач придуманы общие алгоритмы.

Может, на питоне даже есть библиотеки с такими алгоритмами? Что характерно, действительно есть!  
Качаем себе [python-constraint](https://labix.org/python-constraint).

Добавляем цифры и буквы в качестве допустимых значений, создаем переменные
и устанавливаем зависимости между ними.

```python
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
```

Дальше алгоритм все делает за нас.

Осталось только отправить ответы:

```python
    answers = find_answers(r1, r2, r3, r4)

    print(answers)

    payload = " ".join(answers[f'v{i}'] for i in range(1, 5)) + '\n'
    print(payload)
    r.send(payload)
    sleep(0.1)
    for line in r.recvlines(5):
        print(line.decode('utf-8'))
```

Запускаем и получаем флаг после 150 капчи.
