def reduce(amount=[0,0,0,0,0]):
    result = amount.copy()

    while result[4] >= 9:
        result[4] -= 9
        result[3] += 1

    while result[2] >= 4:
        result[2] -= 4
        result[1] += 1

    while result[1] >= 9:
        result[1] -= 9
        result[0] += 1

    return result

def add(amount1=[0,0,0,0,0], amount2=[0,0,0,0,0]):
    result = amount1.copy()
    for i in range(5):
        result[i] += amount2[i]

    result = reduce(result)

    return result

def subtract(amount1=[0,0,0,0,0], amount2=[0,0,0,0,0]):
    result = amount1.copy()
    for i in range(5):
        result[i] -= amount2[i]

    while result[2] < 0:
        result[1] -= 1
        result[2] += 4

    while result[1] < 0:
        result[0] -= 1
        result[1] += 9

    while result[4] < 0:
        result[3] -= 1
        result[4] += 9

    return result

def lessthan(amount1=[0,0,0,0,0], amount2=[0,0,0,0,0]):
    testlist = subtract(amount1, amount2)
    result = all(i <= 0 for i in testlist)
    return result

def greaterthan(amount1=[0,0,0,0,0], amount2=[0,0,0,0,0]):
    result = not lessthan(amount1, amount2)
    return result