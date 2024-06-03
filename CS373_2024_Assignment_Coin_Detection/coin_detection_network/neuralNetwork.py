import numpy
import scipy.special

class neuralNetwork:
    
    def __init__(self, inputnodes, hiddennodes, outputnodes, learningrate) :
        self.In = inputnodes
        self.Hid = hiddennodes
        self.Out = outputnodes
        self.Lr = learningrate
        # create weight matrices, wih and who with random normal distribution 
        self.wih = numpy.random.normal(0.0, pow(self.Hid, -0.5), (self.Hid, self.In))
        self.who = numpy.random.normal(0.0, pow(self.Out, -0.5), (self.Out, self.Hid))
        # define activation function 
        self.activation_function = lambda x: scipy.special.expit(x)
        self.reverse_activation_function = lambda x: scipy.special.logit(x)
        
    def train(self, input_list, target_list):        
        inputs = numpy.array(input_list, ndmin=2).T
        targets = numpy.array(target_list, ndmin=2).T
        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        output_errors = targets - final_outputs
        hidden_errors = numpy.dot(self.who.T, output_errors)
        self.who += self.Lr * numpy.dot((output_errors * final_outputs * (1.0 - final_outputs)), numpy.transpose(hidden_outputs))
        self.wih += self.Lr * numpy.dot((hidden_errors * hidden_outputs * (1.0 - hidden_outputs)), numpy.transpose(inputs))
        
    def query(self,input_list):
        inputs = numpy.array(input_list, ndmin=2).T
        hidden_inputs = numpy.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)
        final_inputs = numpy.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        
        return final_outputs
    
    def reverse(self,output_list):
        outputs = numpy.array(output_list, ndmin=2).T
        final_inputs = numpy.dot(self.who.T, outputs)
        final_outputs = self.reverse_activation_function(final_inputs)
        hidden_inputs = numpy.dot(self.wih.T, final_outputs)
        hidden_outputs = self.reverse_activation_function(hidden_inputs)
        inputs = numpy.dot(self.who.T, hidden_outputs)
        return inputs