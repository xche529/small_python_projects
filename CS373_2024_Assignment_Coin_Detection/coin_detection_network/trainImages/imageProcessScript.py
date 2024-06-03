from PIL import Image
import numpy as np
import os
import matplotlib.pyplot as plt
import copy


def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):
    new_pixel_array = []
    for _ in range(image_height):
        new_row = []
        for _ in range(image_width):
            new_row.append(initValue)
        new_pixel_array.append(new_row)

    return new_pixel_array


def convert_to_greyscale(px_array_r, px_array_g, px_array_b, image_width, image_height):
    # Create a new pixel array for the greyscale image
    px_array = createInitializedGreyscalePixelArray(image_width, image_height)
    
    # Loop through all pixels in the pixel arrays
    for y in range(len(px_array_r)):
        for x in range(len(px_array_r[y])):
            # Convert the RGB pixel to greyscale
            px_array[y][x] = 0.3 * px_array_r[y][x] + 0.6 * px_array_g[y][x] + 0.1 * px_array_b[y][x]
    
    return px_array

def computeCumulativeHistogram(pixel_array, image_width, image_height, nr_bins = 256):
    result = [0] * nr_bins
    for i in range(0,image_height):
        for j in range(0,image_width):
            intensity = pixel_array[i][j]
            for z in range(nr_bins):
                if z >= intensity:
                    result[z] = result[z] + 1
    return result

def computeHistogram(pixel_array, image_width, image_height, nr_bins = 256):
    result = [0] * nr_bins
    for i in range(0,image_height):
        for j in range(0,image_width):
            intensity = round(pixel_array[i][j])
            result[intensity] = result[intensity] + 1
    return result

def computeValueList(pixel_array, image_width, image_height):
    histogram = computeHistogram(pixel_array, image_width, image_height)
    result = []
    for i in range(0,len(histogram)):
        if histogram[i] != 0:
            result.append([i, histogram[i]])
    return result

def findSmallLarge(pixel_array, image_width, image_height, nr_bins = 256):
    cumulativeHistogram = computeCumulativeHistogram(pixel_array, image_width, image_height, nr_bins)
    total = image_width * image_height
    smallNumber = total * 0.05
    largeNumber = total * 0.95
    large = 0
    small = 0
    for i in range(0,nr_bins):
        if cumulativeHistogram[i] > smallNumber:
            small = i
            break
    for i in range(nr_bins-1,-1,-1):
        if cumulativeHistogram[i] < largeNumber:
            large = i
            break
    return (small, large)


def scaleTo0And255AndQuantize(pixel_array, image_width, image_height):
    result = pixel_array
    (min_p, max_p) = findSmallLarge(pixel_array, image_width, image_height)
    for i in range(0,image_height):
        for j in range(0,image_width):
            if max_p == min_p:
                s = round(pixel_array[i][j] - min_p)
            else:
                s = round((pixel_array[i][j] - min_p) * (255 / (max_p - min_p)))
            if s < 0:
                result[i][j] = 0
            elif s > 255:
                result[i][j] = 255
            else:
                result[i][j] = s
    return result

def applyFilter(pixel_array, image_width, image_height, filter):
    hight = len(filter)
    width = len(filter[0])
    result_array = createInitializedGreyscalePixelArray(image_width, image_height)
    for i in range(image_height):
        for j in range(image_width):
            # set border ignore
            if i > hight // 2 - 1 and i < image_height - hight // 2 and j > width // 2 - 1 and j < image_width - width // 2:
                result_array[i][j] = applyFilterToPixel(pixel_array, i, j, filter)
            else:
                result_array[i][j] = 0.0

    return result_array

def applyFilterToPixel(pixel_array, i, j, filter):
    hight = len(filter)
    width = len(filter[0])
    pixelValue = 0.0
    for x in range(hight):
        for y in range(width):
            if filter[x][y] == 0:
                continue
            pixelValue = pixelValue + pixel_array[i - hight // 2 + x][j - width // 2 + y] * filter[x][y]
            
    # if pixelValue<0:
    #     pixelValue = pixelValue * -1
    return pixelValue

def getTwoDArrayAbsSum(arrayOne, arrayTwo):
    result = createInitializedGreyscalePixelArray(len(arrayOne[0]), len(arrayOne))
    for i in range(len(arrayOne)):
        for j in range(len(arrayOne[0])):
            result[i][j] = abs(arrayOne[i][j]) + abs(arrayTwo[i][j])
    return result

def computeAdaptiveThresholdGE(pixel_array, image_width, image_height):
    valueList = computeValueList(pixel_array, image_width, image_height)
    j_value = thresholdAdaptationInitialisation(valueList)
    for i in range(1, len(valueList)):
        jPlusOne = thresholdAdaptationIteration(valueList, i)
        if jPlusOne == j_value:
            break
        j_value = jPlusOne
    if j_value < 225:
        j_value = j_value * 1.5
    print(j_value)
    result = computeThresholdGE(pixel_array, image_width, image_height, j_value)
    return result

def computeThresholdGE(pixel_array, image_width, image_height, threshold):
    result = pixel_array
    for i in range(0,image_height):
        for j in range(0,image_width):
            if pixel_array[i][j] < threshold:
                result[i][j] = 0
            else:
                result[i][j] = 255
    return result

def computeAdaptiveThresholdMethodTwo(pixel_array, image_width, image_height):
    cumulativeHistogram = computeCumulativeHistogram(pixel_array, image_width, image_height)
    pixel_number = image_width * image_height
    for i in range(0,len(cumulativeHistogram)):
        number = cumulativeHistogram[i]
        if number >= pixel_number * 0.5:
            break
    result = computeThresholdGE(pixel_array, image_width, image_height, i)
    return result
    
    
def thresholdAdaptationInitialisation(valueList):
    count = 0
    sum = 0
    for i in range(len(valueList)):
        count = count + valueList[i][1]
        sum = sum + valueList[i][0] * valueList[i][1]
    result = sum / count
    return result

def thresholdAdaptationIteration(valueList, j):
    sumS = 0
    sumB = 0
    countS = 0
    countB = 0
    length = len(valueList)
    if j >= length:
        return 0
    for i in range(length):
        if i < j:
            countS = countS + valueList[i][1]
            sumS = sumS + valueList[i][0] * valueList[i][1]
        else:
            countB = countB + valueList[i][1]
            sumB = sumB + valueList[i][0] * valueList[i][1]
    result = round((sumS / countS + sumB / countB) / 2)
    return result
        

def computeDilation8Nbh3x3FlatSE(pixel_array, image_width, image_height, kernel):
    result_array = copy.deepcopy(pixel_array)
    for i in range(image_height):
        for j in range(image_width):
                if checkHit(pixel_array, i, j, kernel):
                    result_array[i][j] = 1

    return result_array


def checkHit(pixel_array, i, j, kernel):
    imageWidth = len(pixel_array[0])
    imageHeight = len(pixel_array)
    height = len(kernel)
    width = len(kernel[0])
    for x in range(height):
        for y in range(width):
            if kernel[x][y] == 0:
                continue
            # Assume border padding is 0
            elif i - height // 2 + x < 0 or i - height // 2 + x >= imageHeight or j - width // 2 + y < 0 or j - width // 2 + y >= imageWidth:
                continue
            elif pixel_array[i - height // 2 + x][j - width // 2 + y] != 0:
                return True
    return False

def computeErosion8Nbh3x3FlatSE(pixel_array, image_width, image_height, kernel):
    result_array = copy.deepcopy(pixel_array)
    for i in range(image_height):
        for j in range(image_width):
                if checkFit(pixel_array, i, j, kernel):
                    result_array[i][j] = 1
                else:
                    result_array[i][j] = 0

    return result_array

def checkFit(pixel_array, i, j, kernel):
    imageWidth = len(pixel_array[0])
    imageHeight = len(pixel_array)
    height = len(kernel)
    width = len(kernel[0])   
    for x in range(height):
        for y in range(width):
            if kernel[x][y] == 0:
                continue
            elif i - height // 2 + x < 0 or i - height // 2 + x >= imageHeight or j - width // 2 + y < 0 or j - width // 2 + y >= imageWidth:
                return False
            elif pixel_array[i - height // 2 + x][j - width // 2 + y] == 0:
                return False
    return True
                 

def getMinMaxXY(pixel_array, image_width, image_height, ID):
    max_x = 0
    max_y = 0
    min_x = image_width
    min_y = image_height
    for i in range(image_height):
        for j in range(image_width):
            if pixel_array[i][j] == ID:
                if i > max_y:
                    max_y = i
                if i < min_y:
                    min_y = i
                if j > max_x:
                    max_x = j
                if j < min_x:
                    min_x = j
    return [min_x, min_y, max_x, max_y]

def getColorImage(pixel_array_r, pixel_array_g, pixel_array_b, image_width, image_height):
    result = []
    for i in range(image_height):
        row = []
        for j in range(image_width):
            row.append([pixel_array_r[i][j], pixel_array_g[i][j], pixel_array_b[i][j]])
        result.append(row)
    return result

def getLaplacianFilter():
    return [[1, 1, 1],
            [1, -8, 1],
            [1, 1, 1]]
    
def getKernel():
    return [[0, 0, 1, 0, 0], 
            [0, 1, 1, 1, 0], 
            [1, 1, 1, 1, 1], 
            [0, 1, 1, 1, 0], 
            [0, 0, 1, 0, 0]]

def getHorizontalScharrFilter():
    return [[3/32, 0, -3/32], [10/32, 0, -10/32], [3/32, 0, -3/32]]

def getVerticalScharrFilter():
    return [[3/32, 10/32, 3/32], [0, 0, 0], [-3/32, -10/32, -3/32]]

def getMeanFilter():
    return [[1/25, 1/25, 1/25, 1/25, 1/25], 
            [1/25, 1/25, 1/25, 1/25, 1/25], 
            [1/25, 1/25, 1/25, 1/25, 1/25], 
            [1/25, 1/25, 1/25, 1/25, 1/25], 
            [1/25, 1/25, 1/25, 1/25, 1/25]]
#row_folder = input("Enter the path to the folder containing the raw images: ")
#target_number = input("Enter the ID these images are of: ")
#target_folder = input("Enter the path to the folder you want to save the processed images to: ")

row_folder = "coin_detection_network/trainImages/50C"
target_number = 5
target_folder = "coin_detection_network/trainImages/Third"

next_suffix = 0


for filename in os.listdir(row_folder):
    # Check if the file is an image (JPEG, PNG, etc.)
    if filename.endswith('.png'):
        # Construct the complete file path
        file_path = os.path.join(row_folder, filename)
        # Open the image
        image = Image.open(file_path).convert('L')
        resized_image = image.resize((70, 70))
        image_array = np.array(resized_image)
        px_array = image_array.tolist()
        image_height = len(px_array)
        image_width = len(px_array[0])
        
        px_array = scaleTo0And255AndQuantize(px_array, image_width, image_height)
        px_array = computeAdaptiveThresholdMethodTwo(px_array, image_width, image_height)    
        image_array = np.array(px_array, dtype=np.uint8)

        image = Image.fromarray(image_array, mode='L')
        next_suffix += 1
        filename = f'{next_suffix}_processed_image_{target_number}.png'
        save_path = os.path.join(target_folder, filename)
        image.save(save_path)
        resized_image.close()
        image.close()

print("Done!")
        

