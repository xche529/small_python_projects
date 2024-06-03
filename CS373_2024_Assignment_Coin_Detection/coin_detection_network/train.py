import neuralParameters as np
import numpy
import json
#this is the script where you can train the neural network 

# train_file_name = input("Enter the name of the file containing the training data: ")
train_file_name = "coin_detection_network/train_data.csv"
train_file = open(train_file_name, 'r')
train_list = train_file.readlines()
train_file.close()

# weight_file_name = input("Enter the name of the file you have the weight: ")
weight_file_name = "coin_detection_network/coin.json"
with open(weight_file_name, 'r') as file:
    weight_list = json.load(file)
    wih = weight_list[0]
    who = weight_list[1]

n = np.create()
n.who = numpy.array(who)
n.wih = numpy.array(wih)


#training process
for image in train_list:
    all_values = image.split(',')
    scaled_input = (numpy.asfarray(all_values[1:]) / 255.0 * 0.99) + 0.01
    #create the target output values (all 0.01, except the desired label which is 0.99)
    targets = numpy.zeros(6) + 0.01
    targets[int(all_values[0])] = 0.99
    n.train(scaled_input, targets)
pass

wih = n.wih.tolist()
who = n.who.tolist()

weight = [wih, who]
with open(weight_file_name, 'w') as file:
    json.dump(weight, file)
print("Done!")
