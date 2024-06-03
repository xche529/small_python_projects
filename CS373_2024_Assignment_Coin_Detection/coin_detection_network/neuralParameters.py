from neuralNetwork import neuralNetwork

#the input is 40*40 grey scale image
i = 4900
#five coin type and one not a coin type
o = 6

#hidden layer node number
h = 200

#learning rate
Lr = 0.01
n = neuralNetwork(i, h, o, Lr)
def i() :
    return i

def o() :
    return o

def h() : 
    return h

def Lr() :
    return Lr

def create():
    return n