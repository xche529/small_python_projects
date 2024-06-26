# Built in packages
import sys
import json
import copy
import numpy
from coin_detection_network.neuralNetwork import neuralNetwork
from PIL import Image

# Matplotlib will need to be installed if it isn't already. This is the only package allowed for this base part of the 
# assignment.
from matplotlib import pyplot
from matplotlib.patches import Rectangle

# import our basic, light-weight png reader library
import imageIO.png

class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

# Define constant and global variables
TEST_MODE = False    # Please, DO NOT change this variable!

def readRGBImageToSeparatePixelArrays(input_filename):
    image_reader = imageIO.png.Reader(filename=input_filename)
    # png reader gives us width and height, as well as RGB data in image_rows (a list of rows of RGB triplets)
    (image_width, image_height, rgb_image_rows, rgb_image_info) = image_reader.read()

    print("read image width={}, height={}".format(image_width, image_height))
    # our pixel arrays are lists of lists, where each inner list stores one row of greyscale pixels
    pixel_array_r = []
    pixel_array_g = []
    pixel_array_b = []

    for row in rgb_image_rows:
        pixel_row_r = []
        pixel_row_g = []
        pixel_row_b = []
        r = 0
        g = 0
        b = 0
        for elem in range(len(row)):
            # RGB triplets are stored consecutively in image_rows
            if elem % 3 == 0:
                r = row[elem]
            elif elem % 3 == 1:
                g = row[elem]
            else:
                b = row[elem]
                pixel_row_r.append(r)
                pixel_row_g.append(g)
                pixel_row_b.append(b)

        pixel_array_r.append(pixel_row_r)
        pixel_array_g.append(pixel_row_g)
        pixel_array_b.append(pixel_row_b)
    
    return (image_width, image_height, pixel_array_r, pixel_array_g, pixel_array_b)

# a useful shortcut method to create a list of lists based array representation for an image, initialized with a value
def createInitializedGreyscalePixelArray(image_width, image_height, initValue = 0):
    new_pixel_array = []
    for _ in range(image_height):
        new_row = []
        for _ in range(image_width):
            new_row.append(initValue)
        new_pixel_array.append(new_row)

    return new_pixel_array


###########################################
### You can add your own functions here ###
###########################################



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

def computeThresholdGE(pixel_array, image_width, image_height, threshold):
    result = pixel_array
    for i in range(0,image_height):
        for j in range(0,image_width):
            if pixel_array[i][j] < threshold:
                result[i][j] = 0
            else:
                result[i][j] = 255
    return result


def computeAdaptiveThresholdGE(pixel_array, image_width, image_height):
    valueList = computeValueList(pixel_array, image_width, image_height)
    j_value = thresholdAdaptationInitialisation(valueList)
    for i in range(len(valueList),1,-1):
        jPlusOne = thresholdAdaptationIteration(valueList, i)
        if jPlusOne == j_value:
            break
        j_value = jPlusOne
    j_value = round(j_value * 0.4)
    print(j_value)
    result = computeThresholdGE(pixel_array, image_width, image_height, j_value)
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
        
def computeAdaptiveThresholdMethodTwo(pixel_array, image_width, image_height):
    cumulativeHistogram = computeCumulativeHistogram(pixel_array, image_width, image_height)
    pixel_number = image_width * image_height
    for i in range(0,len(cumulativeHistogram)):
        number = cumulativeHistogram[i]
        if number >= pixel_number * 0.3:
            break
    result = computeThresholdGE(pixel_array, image_width, image_height, i)
    return result

import copy

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

def computeConnectedComponentLabeling(pixel_array, image_width, image_height):
    
    result_array = copy.deepcopy(pixel_array)
    for i in range(image_height):
        for j in range(image_width):
            if not pixel_array[i][j] == 0:
                result_array[i][j] = -1


    ID = 1
    resultDict = {}
    for i in range(image_height):
        for j in range(image_width):
            if result_array[i][j] == -1:
                 size = treverseComponent(result_array, image_width, image_height, i, j, ID)
                 resultDict[ID] = size
                 ID = ID + 1
    return(result_array, resultDict)
                 
def treverseComponent(result_array, image_width, image_height, i, j, ID):
    size = 0
    travelQueue = Queue()
    travelQueue.enqueue([i,j])
    while not travelQueue.isEmpty():
        [i, j] = travelQueue.dequeue()
        if not result_array[i][j] == -1:
            continue
        size = size + 1
        result_array[i][j] = ID
        if i - 1 > 0:
            if result_array[i - 1][j] == -1:
                travelQueue.enqueue([i - 1,j])
        if j - 1 > 0:
            if result_array[i][j - 1] == -1:
                travelQueue.enqueue([i, j - 1])
        if i + 1 < image_height:
            if result_array[i + 1][j] == -1:
                travelQueue.enqueue([i + 1, j])
        if j + 1 < image_width:
            if result_array[i][j + 1] == -1:
                travelQueue.enqueue([i, j + 1])
                
    return size

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

def getCropedImage(pixel_array,image_width, image_height, min_x, min_y, max_x, max_y):
    result = []
    for i in range(image_height):
        if i < min_y or i > max_y:
            continue
        row = []
        for j in range(image_width):
            if j < min_x or j > max_x:
                continue
            row.append(pixel_array[i][j])
        result.append(row)
    return result

def getResultInRatioRange(resultDict,result_array, image_width, image_height):
    result = {}
    for key in resultDict:
        [min_x, min_y, max_x, max_y] = getMinMaxXY(result_array, image_width, image_height, key)
        ratio = (max_x - min_x) / (max_y - min_y)
        if ratio < 1.1 and ratio > 0.9:
            result[key] = resultDict[key]
    return result

def getRidOfSmallComponent(resultDict):
    result = {}
    for key in resultDict:
        if resultDict[key] > 5000:
            result[key] = resultDict[key]
    return result

def checkCoinType(resultDict, imageArray, result_array):
    weigth_file_name = "coin_detection_network/coin.json"
    result = {}
    
    for key in resultDict:
        [min_x, min_y, max_x, max_y] = getMinMaxXY(result_array, len(imageArray[0]), len(imageArray), key)
        print(min_x, min_y, max_x, max_y)
        px_array = getCropedImage(imageArray, len(imageArray[0]), len(imageArray), min_x, min_y, max_x, max_y)

        image_array = numpy.array(px_array, dtype=numpy.uint8)
        image = Image.fromarray(image_array, mode='L')
        
        # Resize the image to 70x70
        image = image.resize((70, 70))
        px_array = numpy.array(image)
        px_array = px_array.tolist()
        image_height = len(px_array)
        image_width = len(px_array[0])

        # Preprocess the image
        px_array = scaleTo0And255AndQuantize(px_array, image_width, image_height)
        px_array = computeAdaptiveThresholdMethodTwo(px_array, image_width, image_height)    

        image_array = numpy.array(px_array, dtype=numpy.uint8)
        image = Image.fromarray(image_array, mode='L')

        pixels = image.getdata()
        reversedPixels = [abs(255 - pixel) for pixel in pixels]
        px_array = numpy.reshape(reversedPixels,(70,70))
        px_array = px_array.tolist()

        pyplot.imshow(px_array, cmap='gray', aspect='equal')

        # Test the image
        with open(weigth_file_name, 'r') as file:
            weight_list = json.load(file)
            wih = weight_list[0]
            who = weight_list[1]
        n = neuralNetwork(4900, 200, 6, 0.2)
        n.who = numpy.array(who)
        n.wih = numpy.array(wih)

        scaled_input = (numpy.asfarray(reversedPixels) / 255.0 * 0.99) + 0.01
        outputs = n.query(scaled_input)
        label = numpy.argmax(outputs)
        outputs_list = outputs.tolist()
        test_result = [label, outputs_list[label]]
        result[key] = test_result
        
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
    
# This is our code skeleton that performs the coin detection.
def main(input_path, output_path):
    # This is the default input image, you may change the 'image_name' variable to test other images.
    image_name = 'easy_case_6'
    input_filename = f'./Images/easy/{image_name}.png'
    if TEST_MODE:
        input_filename = input_path 

    # we read in the png file, and receive three pixel arrays for red, green and blue components, respectively
    # each pixel array contains 8 bit integer values between 0 and 255 encoding the color values
    (image_width, image_height, px_array_r, px_array_g, px_array_b) = readRGBImageToSeparatePixelArrays(input_filename)
    
    ###################################
    ### STUDENT IMPLEMENTATION Here ###
    ###################################
    
    
    greyscale = convert_to_greyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)

    scaled_array = scaleTo0And255AndQuantize(greyscale, image_width, image_height)
    horizontalEdge = applyFilter(scaled_array, image_width, image_height, getHorizontalScharrFilter())
    verticalEdge = applyFilter(scaled_array, image_width, image_height, getVerticalScharrFilter())
    px_array = getTwoDArrayAbsSum(verticalEdge,horizontalEdge)
    px_array = applyFilter(px_array, image_width, image_height, getMeanFilter())
    px_array = applyFilter(px_array, image_width, image_height, getMeanFilter())
    px_array = applyFilter(px_array, image_width, image_height, getMeanFilter())

    px_array = computeAdaptiveThresholdGE(px_array, image_width, image_height)

    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())

    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())

    (result_array, resultDict) = computeConnectedComponentLabeling(px_array, image_width, image_height)
    resultDict = getRidOfSmallComponent(resultDict)
    resultDict = getResultInRatioRange(resultDict, result_array, image_width, image_height)
    coinNumber = len(resultDict)
    typeDict = checkCoinType(resultDict, greyscale, result_array)
    
    bounding_box_list = []
    for key in resultDict:
        locationList = getMinMaxXY(result_array, image_width, image_height, key)
        typeList = typeDict[key]
        coinType = typeList[0]
        if coinType == 0:
            coinType = "Not a coin"
        elif coinType == 1:
            coinType = "1 dollor"
        elif coinType == 2:
            coinType = "2 dollor"
        elif coinType == 3:
            coinType = "10 cent"
        elif coinType == 4:
            coinType = "20 cent"
        elif coinType == 5:
            coinType = "50 cent"
        
        parablity = typeList[1]
        print(parablity)
        coinType = f"{coinType} {round(parablity[0], 2)}"
        locationList.append(coinType)
        bounding_box_list.append(locationList)
        print(key, bounding_box_list[-1])
    
    px_array = getColorImage(px_array_r, px_array_g, px_array_b, image_width, image_height)
    
    
    
    
    ############################################
    ### Bounding box coordinates information ###
    ### bounding_box[0] = min x
    ### bounding_box[1] = min y
    ### bounding_box[2] = max x
    ### bounding_box[3] = max y
    ############################################
    
    #bounding_box_list = [[150, 140, 200, 190]]  # This is a dummy bounding box list, please comment it out when testing your own code.

    fig, axs = pyplot.subplots(1, 1)
    axs.imshow(px_array, aspect='equal')
    
    # Loop through all bounding boxes
    for bounding_box in bounding_box_list:
        bbox_min_x = bounding_box[0]
        bbox_min_y = bounding_box[1]
        bbox_max_x = bounding_box[2]
        bbox_max_y = bounding_box[3]
        
        bbox_xy = (bbox_min_x, bbox_min_y)
        bbox_width = bbox_max_x - bbox_min_x
        bbox_height = bbox_max_y - bbox_min_y
        rect = Rectangle(bbox_xy, bbox_width, bbox_height, linewidth=2, edgecolor='r', facecolor='none')
        axs.add_patch(rect)
        
        label_x = bbox_min_x
        label_y = bbox_min_y - 10  # Adjust the y position to place the label above the box
        axs.text(label_x, label_y, bounding_box[4], color='red', fontsize=12, fontweight='bold')
        
    axs.text(5, image_height - 5, "coin count:" + str(coinNumber), color='red', fontsize=12, fontweight='bold')
    pyplot.axis('off')
    pyplot.tight_layout()
    default_output_path = f'./output_images/{image_name}_with_bbox.png'
    if not TEST_MODE:
        # Saving output image to the above directory
        pyplot.savefig(default_output_path, bbox_inches='tight', pad_inches=0)
        
        # Show image with bounding box on the screen
        pyplot.imshow(px_array, cmap='gray', aspect='equal')

        pyplot.show()
    else:
        # Please, DO NOT change this code block!
        pyplot.savefig(output_path, bbox_inches='tight', pad_inches=0)



if __name__ == "__main__":
    num_of_args = len(sys.argv) - 1
    
    input_path = None
    output_path = None
    if num_of_args > 0:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        TEST_MODE = True
    
    main(input_path, output_path)
    