import math

def sportsbook_convert(p):
    if p >= 1.00:
        return '--'

    if p > 0.85:
        p *= max(1.316 - 0.314*p, 1.01)
    else:
        p *= 1.05
    
    if p >= 1.00:
        x = 100000
    elif p >= 0.5:
        x = 100*p/(1-p)
    elif p > 0:
        x = 100/p - 100
    else:
        return '--'

    rnd = math.floor if p < 0.5 else math.ceil
    sign = '+' if p < 0.5 else '-'
    if x < 400:
        x = 10 * rnd(x/10)
    elif x < 1000:
        x = 50 * rnd(x/50)
    elif x < 4000:
        x = 100 * rnd(x/100)
    elif x < 10000:
        x = 500 * rnd(x/500)
    elif x < 40000:
        x = 1000 * rnd(x/1000)
    elif x < 100000:
        x = 10000 * rnd(x/10000)
    else:
        x = 100000

    return sign + str(x)