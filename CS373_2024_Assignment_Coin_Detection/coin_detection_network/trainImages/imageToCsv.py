import csv
from PIL import Image
import os

# name = input("Enter the name of the CSV file you want: ")
# pic_folder = input("Enter the path to the folder containing the images: ")

name = 'train_data'
pic_folder = "coin_detection_network/trainImages/Third"
csv_file = name + '.csv'

for filename in os.listdir(pic_folder):
    if filename.endswith('.png'):
        #get the ID the image is of
        id = filename[-5]
        image = Image.open(os.path.join(pic_folder, filename))
        image = image.convert('L')
        pixels = image.getdata()
        image.close()
        image_data = [id]
        #reverse the image
        for pixel in pixels:
            image_data.append(abs(255 - pixel))
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(image_data)
file.close()
print("Done!")