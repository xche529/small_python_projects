import json
import neuralParameters as np
import os

try:
    n = np.create()

    # file_name = input("Enter the name of the file you want to save the Network to: ")
    file_name = 'coin.json'

    wih = n.wih.tolist()
    who = n.who.tolist()
    weight = [wih, who]

    with open(file_name, 'w') as file:
        json.dump(weight, file)
    
    print("Done!")
except Exception as e:
    print("Error occurred:", e)

print("Current working directory:", os.getcwd())
