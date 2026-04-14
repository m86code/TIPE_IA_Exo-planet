L = [[2,1,0.0,-2],[2.5,0.0],[1.75],[7.125]]
L2 = [4,6,7,8,8,8,9,7]
def poms(nmb,elt):
    return nmb-(elt/2),nmb+(elt/2)

def moyenne(a,b):
    return (a+b)/2

def haar(a,b):
    return -a +b

def compression(L,r=3):
    if len(L)==1:
        return [L]
    res, moy = [], []
    for i in range(0, len(L)-1, 2):
        a = L[i]
        b = L[i+1]
        moy.append(moyenne(a,b))
        res.append(haar(a,b))
    return [res] + compression(moy)

def decompression(E):
    S = []
    C,F = E[:-1],E[-1]
    for i in range(len(C)):
        for j in range(len(C[len(C)-i-1])):
            a,b = poms(F[j],C[len(C)-i-1][j])
            S += [a,b]
        F = S
        S = []
    return F

from random import randint
L = [randint(0,100) for _ in range(2**21)]
a = decompression(compression(L))
#print(a)
#print(L)
print(L == a)
