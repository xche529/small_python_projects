# Built in packages
import math
import sys
import copy

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

def computeThresholdGE(pixel_array, threshold_value, image_width, image_height):
    result = pixel_array
    for i in range(0,image_height):
        for j in range(0,image_width):
            if pixel_array[i][j] < threshold_value:
                result[i][j] = 0
            else:
                result[i][j] = 255
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
    
    
    px_array = convert_to_greyscale(px_array_r, px_array_g, px_array_b, image_width, image_height)
    px_array = scaleTo0And255AndQuantize(px_array, image_width, image_height)
    horizontalEdge = applyFilter(px_array, image_width, image_height, getHorizontalScharrFilter())
    verticalEdge = applyFilter(px_array, image_width, image_height, getVerticalScharrFilter())
    px_array = getTwoDArrayAbsSum(verticalEdge,horizontalEdge)
    px_array = applyFilter(px_array, image_width, image_height, getMeanFilter())
    px_array = applyFilter(px_array, image_width, image_height, getMeanFilter())
    px_array = applyFilter(px_array, image_width, image_height, getMeanFilter())
    px_array = computeThresholdGE(px_array, 15, image_width, image_height)
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeDilation8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
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
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    px_array = computeErosion8Nbh3x3FlatSE(px_array, image_width, image_height, getKernel())
    
    (result_array, resultDict) = computeConnectedComponentLabeling(px_array, image_width, image_height)
    bounding_box_list = []
    for key in resultDict:
        bounding_box_list.append(getMinMaxXY(result_array, image_width, image_height, key))
    
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
    