from PIL import Image, ImageDraw
import random
import numpy as np
import csv
import math

def ReadKeys(image):
    """Input an image and its associated SIFT keypoints.

    The argument image is the image file name (without an extension).
    The image is read from the PGM format file image.pgm and the
    keypoints are read from the file image.key.

    ReadKeys returns the following 3 arguments:

    image: the image (in PIL 'RGB' format)

    keypoints: K-by-4 array, in which each row has the 4 values specifying
    a keypoint (row, column, scale, orientation).  The orientation
    is in the range [-PI, PI] radians.

    descriptors: a K-by-128 array, where each row gives a descriptor
    for one of the K keypoints.  The descriptor is a 1D array of 128
    values with unit length.
    """
    im = Image.open(image+'.pgm').convert('RGB')
    keypoints = []
    descriptors = []
    first = True
    with open(image+'.key','rb') as f:
        reader = csv.reader(f, delimiter=' ', quoting=csv.QUOTE_NONNUMERIC,skipinitialspace = True)
        descriptor = []
        for row in reader:
            if len(row) == 2:
                assert first, "Invalid keypoint file header."
                assert row[1] == 128, "Invalid keypoint descriptor length in header (should be 128)."
                count = row[0]
                first = False
            if len(row) == 4:
                keypoints.append(np.array(row))
            if len(row) == 20:
                descriptor += row
            if len(row) == 8:
                descriptor += row
                assert len(descriptor) == 128, "Keypoint descriptor length invalid (should be 128)."
                #normalize the key to unit length
                descriptor = np.array(descriptor)
                descriptor = descriptor / math.sqrt(np.sum(np.power(descriptor,2)))
                descriptors.append(descriptor)
                descriptor = []
    assert len(keypoints) == count, "Incorrect total number of keypoints read."
    print "Number of keypoints read:", int(count)
    return [im,keypoints,descriptors]

def AppendImages(im1, im2):
    """Create a new image that appends two images side-by-side.

    The arguments, im1 and im2, are PIL images of type RGB
    """
    im1cols, im1rows = im1.size
    im2cols, im2rows = im2.size
    im3 = Image.new('RGB', (im1cols+im2cols, max(im1rows,im2rows)))
    im3.paste(im1,(0,0))
    im3.paste(im2,(im1cols,0))
    return im3

def DisplayMatches(im1, im2, matched_pairs):
    """Display matches on a new image with the two input images placed side by side.

    Arguments:
     im1           1st image (in PIL 'RGB' format)
     im2           2nd image (in PIL 'RGB' format)
     matched_pairs list of matching keypoints, im1 to im2

    Displays and returns a newly created image (in PIL 'RGB' format)
    """
    im3 = AppendImages(im1,im2)
    offset = im1.size[0]
    draw = ImageDraw.Draw(im3)
    for match in matched_pairs:
        draw.line((match[0][1], match[0][0], offset+match[1][1], match[1][0]),fill="red",width=2)
    im3.show()
    return im3

def match(image1,image2):
    """Input two images and their associated SIFT keypoints.
    Display lines connecting the first 5 keypoints from each image.
    Note: These 5 are not correct matches, just randomly chosen points.

    The arguments image1 and image2 are file names without file extensions.

    Returns the number of matches displayed.

    Example: match('scene','book')
    """
    im1, keypoints1, descriptors1 = ReadKeys(image1)
    im2, keypoints2, descriptors2 = ReadKeys(image2)
    #
    # REPLACE THIS CODE WITH YOUR SOLUTION (ASSIGNMENT 5, QUESTION 3)
    #
    #Generate five random matches (for testing purposes)
    matched_pairs = []
    #keypoints1 and 2 = array of keypoints
    for x in range(len(descriptors1)):
        angles = []
        for y in range(len(descriptors2)):
            #find the angle between the two discriptors - take the inverse cosine of the dot product of the two
            dot_prod = np.dot(descriptors1[x], descriptors2[y])
            angles.append(math.acos(dot_prod))
        #sort the angles
        sorted_angles= sorted(angles)
        #ratio of angle[0]/angle[1] above a certain threshold will be added to our list
        if((sorted_angles[0]/sorted_angles[1])< 0.77):
            y = angles.index(sorted_angles[0])
            matched_pairs.append([keypoints1[x], keypoints2[y]])

    # Thresholds for angle and size.
    angle_threshold = math.pi/30
    size_threshold = 0.50

    ransac_best = []
    options = []

    #randomly select one of the pairs, 10 times.

    for i in range(10):
        #grab a random match 10 times.
        temp = matched_pairs[random.randrange(len(matched_pairs))]
        #grabbing scale and orientation fields
        scale_0 = (temp[0][2] - temp[1][2])
        orientation_0 = (temp[0][3]- temp[1][3])
        #for each one- iterate through ALL the matched pairs
        for j in range(len(matched_pairs)):
            #grabbing the scale and orientation fields.
            scale_1 = (matched_pairs[j][0][2] - matched_pairs[j][1][2])
            orientation_1 = (matched_pairs[j][0][3] - matched_pairs[j][1][3])
            #find the difference betweent the angles
            angle_diff = orientation_0-orientation_1

            #angle can't be larger than pi.
            if angle_diff > math.pi:
                angle_diff = angle_diff - math.pi

            #scale difference can't be negative
            scale_diff = abs(scale_0-scale_1)

            #if both match threshold - want to add as an option.
            if (angle_diff<=angle_threshold and scale_diff <= size_threshold):
                options.append(matched_pairs[j])
            #if have more options than best matches so far - this is the best option
            if len(options) > len(ransac_best):
                ransac_best = options


    # END OF SECTION OF CODE TO REPLACE
    #
    im3 = DisplayMatches(im1, im2, ransac_best)
    return im3

#Test run...
match('scene','book')
#match('library','library2')

