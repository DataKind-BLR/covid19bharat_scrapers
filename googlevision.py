import re
import io
import os
import cv2
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.patches as patches

from PIL import Image
from fuzzywuzzy import process
from google.cloud import vision
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from googlevision_utils import ColumnHandler


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'visionapi.json'
POLY_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'poly.txt')
OUTPUT_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'output.txt')
OUTPUT_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'image.png')
BOUNDS_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'bounds.txt')
STATES_META = os.path.join(os.path.dirname(__file__), '_meta')


def generate_annotations(img_file):
  '''
  Given an image file, return the annotations using Google vision API

  :param: `img_file` <os.path> - path to the image file

  :return: <annotations Object> - containing co-ordinates for every detected text
  '''
  client = vision.ImageAnnotatorClient()

  with io.open(img_file, 'rb') as img:
    content = img.read()

  image = vision.Image(content=content)
  response = client.document_text_detection(image=image)

  if response.error.message:
    raise Exception(
        '{}\nFor more info on error messages, check: '
        'https://cloud.google.com/apis/design/errors'.format(response.error.message)
    )

  annotations = response.text_annotations
  return annotations


# <<<<<<< HEAD
# def create_obj(ann, ind):
#   '''
#       # [x, y] coordinates for top left of the annotation area
#       # [x, y] coordinates for top right of the annotation area
#       # [x, y] coordinates for bottom left of the annotation area
#       # [x, y] coordinates for bottom right of the annotation area
#       # x - mid point of the width of the annotation area
#       # y - mid point of the height of the annotation area
#       # width of the annotation area
#       # height of the annotation area
#       # index starting from 1 through N (total number of annotations)
#       # column index of the annotation area
#       # row index of the annotation area
#   '''
#   verts = ann.bounding_poly.vertices
#   return {
#     'value':    ann.description,
#     'top_l_x':  verts[0].x,
#     'top_l_y':  verts[0].y,
#     'top_r_x':  verts[1].x,
#     'top_r_y':  verts[1].y,
#     'bot_r_x':  verts[2].x,
#     'bot_r_y':  verts[2].y,
#     'bot_l_x':  verts[3].x,
#     'bot_l_y':  verts[3].y,
#     'x_mean':   (verts[3].x + verts[2].x) / 2,  # x - mid point of the width of the annotation area
#     'y_mean':   (verts[3].y + verts[0].y) / 2,  # y - mid point of the height of the annotation area
#     'width':    verts[2].x - verts[3].x,        # width of the annotation area
#     'height':   verts[3].y - verts[0].y,        # height of the annotation area
#     'index':    ind                             # index starting from 1 through N (total number of annotations)
#   }


# def get_same_row_numbers(d_row, nums_df):
#   '''
#   Given a district row, get all numbers on the same row from the numbers dataframe
#   '''
#   threshold = 2     # +/- 2
#   same_row = nums_df[nums_df['y_mean'].between(d_row['y_mean'] - threshold, d_row['y_mean'] + threshold)]
#   return same_row.sort_values(by='x_mean', ascending=True)['value'].to_list()


def generate(opt):
  '''
  :param: `img_file` <os.path> - path to the image file

  :return: <arr> - containing extracted annotations
  '''
  ## step 1 - generate annotations
  annotations = generate_annotations(opt['url'])

  ## step 2 - write annotations to `poly.txt`
  with io.open(POLY_TXT, 'w') as poly_file:
    print(annotations, file=poly_file)
  poly_file.close()

  ## step 3 - write the extracted verticies and description of every line to `bounds.txt`
  '''
      for every annotation, get x & y vertices of annotations and print in following format
                          |  top l   |   top r  | bottom r |  bottom l
      -> `<desc> | bounds | <x>, <y> | <x>, <y> | <x>, <y> | <x>, <y>


  '''
# <<<<<<< HEAD
#   annotations = generate_annotations(opt['url'])

#   # create 2 arrays, one for `district texts` and other for `numbers`
#   districts_arr = []
#   numbers_arr = []

#   ind = 0
#   for ann in annotations:
#     ind += 1

#     ## SKIP if the description text is larger than 50 chars
#     if len(ann.description) > 50:
#       continue

#     ## If description text is NOT in translation dictionary, then it must be a number
#     if ann.description not in translation_dict.keys():
#       numbers_arr.append(create_obj(ann, ind))        # then append to numbers arr
#     else:
#       districts_arr.append(create_obj(ann, ind))      # else append to discticts arr

#   # create 2 dataframes from the arrays
#   dist_df = pd.DataFrame(districts_arr)
#   nums_df = pd.DataFrame(numbers_arr)

#   for index, dist_row in dist_df.iterrows():
#     row_values = get_same_row_numbers(dist_row, nums_df)
#     row_values.insert(0, dist_row['value'])
#     print(row_values)


#   # TODO -----> if opt['verbose'] == True:
#   ## Write annotations to `poly.txt`
#   with io.open(POLY_TXT, 'w') as poly_file:
#     print(annotations, file=poly_file)
#   poly_file.close()

#   ## Write bound coordinates into `bounds.txt` in a readable format
# =======
  extracted_arr = []
  for text in annotations:
    # extracted = {}
    verts = text.bounding_poly.vertices
    extracted_arr.append({
      'value': text.description,
      'top_l': [verts[0].x, verts[0].y],   # [x, y] coordinates
      'top_r': [verts[1].x, verts[1].y],
      'bot_r': [verts[2].x, verts[2].y],
      'bot_l': [verts[3].x, verts[3].y]
    })

# >>>>>>> parent of 08b5006... WIP (with debugger) - only looping annotations once
  with io.open(BOUNDS_TXT, 'w') as bounds_file:
    for text in annotations:
      vertices = (['{},{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
      print('{}'.format(text.description), end ='|', file=bounds_file)
      print('bounds|{}'.format('|'.join(vertices)), file=bounds_file)

  bounds_file.close()
  return extracted_arr


def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False


def detectLines(img_file, min_line_length, col_handler):
  '''
  Given an image file and
  '''
  img = cv2.imread(img_file)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(img, 50, 150)
  lines = cv2.HoughLinesP(edges, 1, np.pi/135, min_line_length, maxLineGap=250)

  for line in lines:
    x1, y1, x2, y2 = line[0]
    col_handler.addPoint(x1, y1)
    col_handler.addPoint(x2, y2)

  col_handler.prepareColumn()
  col_handler.prepareRow()
  col_handler.printColumnsAndCoordinates()

  return col_handler


def buildCells(extracted_arr, translationDictionary, startingText, endingText, houghTransform, columnHandler):
  xInterval = 0
  yInterval = 0
  xStartThreshold = 0
  yStartThreshold = 0
  xEndThreshold = 0
  yEndThreshold = 0
  xWidthTotal = 0
  maxWidth = 0
  maxHeight = 0
  dataDictionaryArray = []

  startingMatchFound = False
  endingMatchFound = False
  autoEndingText = endingText
  autoStartingText = startingText


  for ext in extracted_arr:
    # calculate x_mean and y_mean
    ext['x_mean'] = (ext['bot_l'][0] + ext['bot_r'][0]) / 2
    ext['y_mean'] = (ext['bot_l'][1] + ext['top_l'][1]) / 2

    # keep track of the x-limit
    x_limit = columnHandler.getNearestLineToTheLeft(xStartThreshold) if houghTransform == True else xStartThreshold - 20

# ------------------------------------------------------------------------------------------------------------------------

  bounds_file = open(BOUNDS_TXT, 'r')

  ## read every line from bounds.txt
  for index, line in enumerate(bounds_file):
    lineArray = line.split('|')

    # skip line if it doesn't exactly contain 6 elements
    if len(lineArray) != 6:
      continue

    if not lineArray[0] or not lineArray[2] or not lineArray[4] or not lineArray[5]:
      continue

    lowerLeft = []
    lowerRight = []
    upperRight = []
    upperLeft = []

    # save extracted values after splitting the line
    value = lineArray[0]
    lowerLeft = lineArray[2].split(',')
    lowerRight = lineArray[3].split(',')
    upperRight = lineArray[4].split(',')
    upperLeft = lineArray[5].split(',')

    # extracted = {}
    # extracted = {
    #   'value':        lineArray[0],
    #   'upper_left':   list(map(lambda x: int(x), lineArray[4].split(','))),   # [x, y]
    #   'upper_right':  list(map(lambda x: int(x), lineArray[5].split(','))),   # [x, y]
    #   'lower_right':  list(map(lambda x: int(x), lineArray[3].split(','))),   # [x, y]
    #   'lower_left':   list(map(lambda x: int(x), lineArray[2].split(',')))    # [x, y]
    # }

    if len(lowerLeft) != 2 or len(lowerRight) != 2 or len(upperRight) != 2 or len(upperLeft) != 2:
      continue

    # Get the mid point of the bound where the text matches
    xMean = (int(lowerLeft[0]) + int(lowerRight[0])) / 2
    yMean = (int(lowerLeft[1]) + int(upperLeft[1])) / 2

    # extracted['x_mean'] = extracted['lower_left'][0] + extracted['lower_right'][0]
    # extracted['y_mean'] = extracted['lower_left'][1] + extracted['upper_left'][1]

    xLimit = columnHandler.getNearestLineToTheLeft(xStartThreshold) if houghTransform == True else xStartThreshold - 20


    # if starting text is not mentioned, pick and assign an extracted object
    if startingText == 'auto':
      if len(value.title()) > 1 and any(value.title() in district for district in list(translationDictionary.keys())):
        if xStartThreshold == 0:
          xStartThreshold = xMean
          autoStartingText = value
        if yStartThreshold == 0:
          yStartThreshold = yMean

        if yMean < yStartThreshold:
          xStartTreshold = xMean
          yStartThreshold = yMean
          autoStartingText = value


    if endingText == 'auto':
      if len(value.title()) > 1 and any(value.title() in district for district in list(translationDictionary.keys())):
        if xEndThreshold == 0:
          xEndThreshold = xMean
        if yEndThreshold == 0:
          yEndThreshold = yMean
          autoEndingText = value

        if yMean > yEndThreshold:
          xEndThreshold = xMean
          yEndThreshold = yMean
          autoEndingText = value

    if ',' in startingText:
      if value.title() in startingText.split(','):# and startingMatchFound == False:
        startingMatchFound = True
        xStartThreshold = xMean
        yStartThreshold = yMean
    else:
      if value.title() == startingText and startingMatchFound == False:
        startingMatchFound = True
        xStartThreshold = xMean
        yStartThreshold = yMean

    if ',' in endingText:
      if value.title() in endingText.split(','):# and endingMatchFound == False:
        endingMatchFound = True
        xEndThreshold = xMean
        yEndThreshold = yMean
    else:
      if value.title() == endingText and endingMatchFound == False:
        endingMatchFound = True
        xEndThreshold = xMean
        yEndThreshold = yMean

    #Use these intervals as a possible error in mid point calculation
    xInterval = (int(lowerRight[0]) - int(lowerLeft[0]))/2 if (int(lowerRight[0]) - int(lowerLeft[0]))/2 > xInterval else xInterval
    yInterval = (int(upperLeft[1]) - int(lowerLeft[1]))/2 if (int(upperLeft[1]) - int(lowerLeft[1]))/2 > yInterval else yInterval
    xWidthTotal = xWidthTotal + int(lowerRight[0]) - int(lowerLeft[0])

    # REDUCE the array size - same as `buildReducedArray`
    # do not append if...
    if yMean < yStartThreshold - 10 or (xLimit is not None and xMean < xLimit):
      continue

    # # do not append if...
    if len(endingText) != 0 and (yMean > yEndThreshold + 10):
      continue

    #                                    (value, x,     y,     lbx,          lby,           w,                                            h,                                          col, row, index):
    # dataDictionaryArray.append(cellItem(value, xMean, yMean, lowerLeft[0], lowerLeft[1], (float(lowerRight[0]) - float(lowerLeft[0])), (float(upperLeft[1]) - float(lowerLeft[1])), 0, 0, index + 1))
    dataDictionaryArray.append({
      'value': value,
      'x': xMean,
      'y': yMean,
      'lbx': lowerLeft[0],
      'lby': lowerLeft[1],
      'w': (float(lowerRight[0]) - float(lowerLeft[0])),
      'h': (float(upperLeft[1]) - float(lowerLeft[1])),
      'col': 0,
      'row': 0,
      'index': index + 1
    })

    maxWidth = (float(lowerRight[0]) - float(lowerLeft[0])) if (float(lowerRight[0]) - float(lowerLeft[0])) > maxWidth else maxWidth
    maxHeight = (float(upperLeft[1]) - float(lowerLeft[1])) if (float(upperLeft[1]) - float(lowerLeft[1])) > maxHeight else maxHeight

  xWidthTotal = xWidthTotal / len(dataDictionaryArray)
  startingText = autoStartingText
  endingText = autoEndingText
  xInterval = maxWidth / 2
  yInterval = maxHeight / 2
  bounds_file.close()

  return {
    'xInterval': xInterval,
    'yInterval': yInterval,
    'dataDictionaryArray': dataDictionaryArray,
    'xStartThreshold': xStartThreshold,
    'yStartThreshold': yStartThreshold
  }


def assignRowsAndColumns(houghTransform, configxInterval, configyInterval, xInterval, yInterval, dataDictionaryArray, columnHandler):

  if configxInterval != 0:
    xInterval = configxInterval
  if configyInterval != 0:
    yInterval = configyInterval

  print('Using computed yInterval: {}, xInterval: {}'.format(yInterval, xInterval))


  ## again looping through the dataDictionaryArray
  for rowIndex, currentCell in enumerate(dataDictionaryArray):

    # make the row number same as index + 1 (i.e. rows will start from 1 through N)
    if currentCell['row'] == 0:
      currentCell['row'] = rowIndex + 1

    for colIndex, restOfTheCells in enumerate(dataDictionaryArray):
      if currentCell['col'] == 0:
        if houghTransform == True:
          currentCell['col'] = columnHandler.getColumnNumber(currentCell)
        else:
          currentCell['col'] = rowIndex + 1

      if restOfTheCells['index'] == currentCell['index']:
        continue

      yUpperBound = currentCell['y'] + yInterval
      yLowerBound = currentCell['y'] - yInterval

      #If the y coordinate matches, the texts lie on the same row
      if restOfTheCells['row'] == 0:
        if yLowerBound <= restOfTheCells['y'] <= yUpperBound:
          restOfTheCells['row'] = rowIndex + 1

      xUpperBound = currentCell['x'] + xInterval
      xLowerBound = currentCell['x'] - xInterval

      #If the x coordinate matches, the texts lie on the same column
      if restOfTheCells['col'] == 0:
        if houghTransform == True:
          restOfTheCells['col'] = columnHandler.getColumnNumber(restOfTheCells)
        elif xLowerBound <= restOfTheCells['x'] <= xUpperBound:
          restOfTheCells['col'] = currentCell['col']


def get_translation_dict(start_key, end_key, translation_meta):
  '''
  :param: `start_key` <str> - start_key as mentioned in the states.yaml file
  :param: `end_key`   <str> - end_key as mentioned in the states.yaml file
  :param: `translation_meta` <os.path> - path to the `<state_code>_districts.meta` file]

  :returns: <dict> - a dictionary containig the text and it's translated value
  '''

  translation_dict = {}

  try:
    with open(translation_meta, 'r') as meta_file:
      for line in meta_file:
        if line.startswith('#'):
          continue

        line_arr = line.strip().split(',')

        if len(start_key) != 0:
          if start_key.strip() == line_arr[1].strip():
            start_key = start_key + ',' + line_arr[0].strip()

        if len(end_key) != 0:
          if end_key.strip() == line_arr[1].strip():
            end_key = end_key + ',' + line_arr[0].strip()

        translation_dict[line_arr[0].strip()] = line_arr[1].strip()
  except:
    pass

  return translation_dict


def save_output(translation_dict, img_file, hough_transform, dataDictionaryArray, xStartThreshold, yStartThreshold, columnHandler):
  outputFile = open(OUTPUT_TXT, 'w')
  xArray = []
  yArray = []

  image = np.array(Image.open(img_file), dtype=np.uint8)
  fig, ax = plt.subplots(1)
  if hough_transform == True:
    for point in columnHandler.pointList:
      if columnHandler.getNearestLineToTheLeft(xStartThreshold) - 5 <= point.x <= columnHandler.getNearestLineToTheLeft(xStartThreshold) + 5:
        circ = Circle((point.x,point.y),5, color='r')
      else:
        circ = Circle((point.x,point.y),4)
      ax.add_patch(circ)

  for i in range(0, len(dataDictionaryArray)):
    outputString = []
    for cell in dataDictionaryArray:
      if cell['row'] == i:
        outputString.append(cell)
    outputString.sort(key=lambda x: x['x'])

    output = ''
    previousCol = -999
    mergedValue = ''

    # <TODO> column verification has to come in here
    # Merge those texts separated by spaces - these have the same column value due to proximity but belong to different objects
    columnList = ''
    for index, value in enumerate(outputString):
      value['value'] = re.sub('\.', '', re.sub(',', '', value['value']))
      if index == 0:
        mergedValue = value['value']
        previousCol = value['col']
        columnList = str(value['col'])
        rect = patches.Rectangle(
          (int(value['lbx']), int(value['lby'])),
          value['w'],
          value['h'],
          linewidth=0.75,
          edgecolor='r',
          facecolor='none'
        )
        ax.add_patch(rect)
        continue

      if value['col'] == previousCol and is_number(value['value']) == False:
        mergedValue = mergedValue + ' ' + value['value'] if len(mergedValue) != 0 else value['value']
        if index == len(outputString) - 1:
          output += mergedValue if len(output) == 0 else ' , ' + mergedValue
      else:
        if index == len(outputString) - 1:
          mergedValue = mergedValue + ', ' + value['value'] if len(mergedValue) != 0 else value['value']

        output += mergedValue if len(output) == 0 else ' , ' + mergedValue
        previousCol = value['col']
        mergedValue = value['value']
        columnList = columnList + ', ' + str(value['col']) if len(columnList) != 0 else str(value['col'])
        rect = patches.Rectangle(
          (int(value['lbx']), int(value['lby'])),
          value['w'],
          value['h'],
          linewidth = 0.75,
          edgecolor = 'r',
          facecolor = 'none'
        )
        ax.add_patch(rect)

    if len(output) > 0:
      outputArray = output.split(',')
      districtIndex = 0
      # If the rows are not numberd, this condition can be skipped. For UP bulletin, this makes sense.
      if(is_number(outputArray[0])):
        districtName = outputArray[1].strip().capitalize()
        distrinctIndex = 1
      else:
        districtName = outputArray[0].strip().capitalize()
        distrinctIndex = 0

      # Do a lookup for district name, if not found, discard the record and print a message.
      try:
        translatedValue = translation_dict[districtName]
        outputString = translatedValue
        for index, value in enumerate(outputArray):
          if index > districtIndex: #and is_number(value):
            outputString += ',' + value.strip()
      except KeyError:
        try:
          fuzzyDistrict = fuzzyLookup(translation_dict,districtName)
          translatedValue = translation_dict[fuzzyDistrict]
        except:
          print('-------------------------------------------------------------')
          print(f'\n====>>Failed to find lookup for {districtName}\n')
          print('-------------------------------------------------------------')
          continue

      outputString = translatedValue
      for index, value in enumerate(outputArray):
        if index > districtIndex:
          outputString += ',' + value.strip()
      print('{} | {}'.format(outputString, columnList), file = outputFile)

  outputFile.close()
  ax.imshow(image)
  plt.savefig(OUTPUT_PNG, dpi=300)


def fuzzyLookup(translation_dict, dist_name):
  '''
  Use fuzzy string match to map incorrect districtnames to the ones in the dictionary

  :param: `translation_dict` <dict> - dictionary containing district mapping from the `<state_code>_districts.meta` file
  :param: `dist_name`        <str> - name of the district to search for

  :return: <str> - closest mapped district name
  '''
  # Score cut-off of 90 seem to be working well for UP
  district = process.extractOne(
    dist_name,
    translation_dict.keys(),
    score_cutoff = 90)[0]
  print(f'WARN : {dist_name} mapped to {district} using Fuzzy Lookup')
  return district


def get_start_end_keys(opt):
  '''
  Given a state code, get start and end text to read from image

  returns <dict> - the starting and ending text
  '''
  to_return = { 'start_key': 'auto', 'end_key': 'auto' }
  if 'config' in opt:
    to_return.update({ 'start_key': opt['config']['start_key'] if 'start_key' in opt['config'] else 'auto' })
    to_return.update({ 'end_key': opt['config']['end_key'] if 'end_key' in opt['config'] else 'auto' })
  return to_return


def get_translation_file(opt):
  '''
  Given a state code, get the path to the translation file
  '''
  state_code = opt['state_code'].lower()
  return os.path.join(STATES_META, f'{state_code}_districts.meta')


def get_hough_transform(opt):
  '''
  Given a state code, get hough transform configurations

  returns <bool> - Defaults to True
  '''
  state_code = opt['state_code'].lower()
  exceptions = {
    'hp': False,
    'br': False,
    'mp': False,
    'mz': False,
    'ut': False,
    'mh': False
  }
  return exceptions[state_code] if state_code in exceptions.keys() else True


def get_min_line_length(opt):
  '''
  Given a state code, return the min line length for tabular lines in images

  returns <int> - the min line length, defaults to `400`
  '''
  state_code = opt['state_code'].lower()
  exceptions = {
    'ap': 300,
    'tn': 500,
    'ml': 250,
    'nl': 250
  }
  return exceptions[state_code] if state_code in exceptions.keys() else 600


def get_xy_interval(opt):
  '''
  Given a state code, return the x and y intervals

  returns <dict> - containing x & y interval numbers
  '''
  state_code = opt['state_code'].lower()
  exceptions = {
    'mh': { 'x': 0, 'y': 15 }
  }
  return exceptions[state_code.lower()] if state_code in exceptions.keys() else { 'x': 0, 'y': 0 }


def run_for_ocr(opt):
  '''
  opt is the dict object from yaml
  config_file refers to the `ocrconfig.meta` file
  '''
  print('--- Step 1: Running ocr_vision.py file to generate _outputs/poly.txt and _outputs/bounds.txt')
  extracted_arr = generate(opt)

  print(extracted_arr)
  import pdb
  pdb.set_trace()

  # set global variables
  start_end_keys   = get_start_end_keys(opt)
  hough_transform  = get_hough_transform(opt)
  translation_file = get_translation_file(opt)
  xy_interval      = get_xy_interval(opt)
  min_line_length  = get_min_line_length(opt)
  img_file         = opt['url']
  config_file      = '_outputs/ocrconfig.meta'
  columnHandler    = ColumnHandler() # default value
  translation_dict = get_translation_dict(start_end_keys['start_key'], start_end_keys['end_key'], translation_file)

  # step 1 - detect the table lines from the image & store them in `columnHandler` object
  if hough_transform == True:
    columnHandler = detectLines(img_file, min_line_length, columnHandler)

  # step 2 - build cells around detected texts
  r_bc = buildCells(extracted_arr, translation_dict, start_end_keys['start_key'], start_end_keys['end_key'], hough_transform, columnHandler)

  assignRowsAndColumns(hough_transform, xy_interval['x'], xy_interval['y'], r_bc['xInterval'], r_bc['yInterval'], r_bc['dataDictionaryArray'], columnHandler)

  # step 4 - extract and write detected texts and numbers into an `output.txt` file
  save_output(translation_dict, opt['url'], hough_transform, r_bc['dataDictionaryArray'], r_bc['xStartThreshold'], r_bc['yStartThreshold'], columnHandler)


if __name__ == '__main__':
  sample_opt = {'name': 'Chhattisgarh', 'state_code': 'CT', 'cowin_code': 7, 'url_sources': ['https://twitter.com/HealthCgGov', 'http://cghealth.nic.in/cghealth17/'], 'type': 'image', 'url': '_inputs/ct.jpeg', 'config': {'translation': True}, 'skip_output': False, 'verbose': False}
  run_for_ocr(sample_opt)
