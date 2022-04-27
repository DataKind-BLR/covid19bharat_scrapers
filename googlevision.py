import re
import cv2
import os
import sys
import json
import ocr_vision
import numpy as np
import matplotlib.patches as patches

from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.patches import Circle


OUTPUT_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'output.txt')
OUTPUT_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'image.png')
BOUNDS_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'bounds.txt')
STATES_META = os.path.join(os.path.dirname(__file__), '_meta')


dataDictionary = {}
dataDictionaryArray = []
xInterval = 0
xStartThreshold = 0
yStartThreshold = 0
xEndThreshold = 0
yEndThreshold = 0
yInterval = 0
fileName = ""
xWidthTotal = 0

def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

class cellItem:
  def __init__(self, value, x, y, lbx, lby, w, h, col, row, index):
    self.value = value
    self.x = x
    self.y = y
    self.col = col
    self.row = row
    self.index = index
    self.lbx = lbx
    self.lby = lby
    self.h = h
    self.w = w

class ColumnHandler:
  def __init__(self):
    self.columnList = []
    self.rowList = []
    self.pointList = []

  def addPoint(self, x, y):
    self.pointList.append(LinePoints(x, y))

  def prepareRow(self):
    rowNumber = 1
    self.pointList.sort(key=lambda y: y.y)
    for index, col in enumerate(self.pointList):
      if index % 2 == 1:
        continue
      if index == 0:
        previousX = col.x
        previousY = col.y
        continue

      if col.y - previousY < 10:
        continue
      self.rowList.append(ColumnAndRow(previousX, previousY, col.x, col.y, rowNumber))
      previousX = col.x
      previousY = col.y
      rowNumber += 1

  def prepareColumn(self):
    columnNumber = 1
    self.pointList.sort(key=lambda x: x.x)
    for index, col in enumerate(self.pointList):
      if index % 2 == 1:
        continue
      if index == 0:
        previousX = col.x
        previousY = col.y
        continue

      if col.x - previousX < 5:
        continue
      self.columnList.append(ColumnAndRow(previousX, previousY, col.x, col.y, columnNumber))
      previousX = col.x
      previousY = col.y
      columnNumber += 1

  def printColumnsAndCoordinates(self):
    print("Column No ... x1,y1 --> x2,y2")
    for column in self.columnList:
      print("c{} ... {},{} --> {},{}".format(column.number, column.x1, column.y1, column.x2, column.y2))
    for row in self.rowList:
      print("r{} ... {},{} --> {},{}".format(row.number, row.x1, row.y1, row.x2, row.y2))

  def getNearestLineToTheLeft(self, xCoordinate):
    for col in self.columnList:
      if xCoordinate > int(col.x1) and xCoordinate < int(col.x2):
        return col.x1
    return 0

  def getColumnNumber(self, cell):
    for col in self.columnList:
      if cell.x > col.x1 and cell.x < col.x2:
        return col.number

class ColumnAndRow:
  def __init__(self, x1, y1, x2, y2, number):
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2
    self.number = number

class LinePoints:
  def __init__(self, x, y):
    self.x = x
    self.y = y


def detectLines():
  global columnHandler
  global configMinLineLength
  img = cv2.imread(fileName)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(img, 50, 150)
  lines = cv2.HoughLinesP(edges, 1, np.pi/135, configMinLineLength, maxLineGap=250)
  columnHandler = ColumnHandler()
  for line in lines:
    x1, y1, x2, y2 = line[0]
    columnHandler.addPoint(x1, y1)
    columnHandler.addPoint(x2, y2)

  columnHandler.prepareColumn()
  columnHandler.prepareRow()
  columnHandler.printColumnsAndCoordinates()


def buildCells(translationDictionary, startingText, endingText):
  global xInterval
  global yInterval
  # global startingText
  # global endingText
  global xStartThreshold
  global yStartThreshold
  global xEndThreshold
  global yEndThreshold
  global configxInterval
  global configyInterval
  global xWidthTotal

  print('xInterval --->', xInterval)
  print('yInterval --->', yInterval)
  print('startingText --->', startingText)
  print('endingText --->', endingText)
  print('xStartThreshold --->', xStartThreshold)
  print('yStartThreshold --->', yStartThreshold)
  print('xEndThreshold --->', xEndThreshold)
  print('yEndThreshold --->', yEndThreshold)
  print('configxInterval --->', configxInterval)
  print('configyInterval --->', configyInterval)
  print('xWidthTotal --->', xWidthTotal)

  startingMatchFound = False
  endingMatchFound = False
  autoEndingText = endingText
  autoStartingText = startingText
  testingNumbersFile = open(BOUNDS_TXT, "r")


  for index, line in enumerate(testingNumbersFile):
    lineArray = line.split('|')
    if len(lineArray) != 6:
      continue

    lowerLeft = []
    lowerRight = []
    upperRight = []
    upperLeft = []

    if not lineArray[0] or not lineArray[2] or not lineArray[4] or not lineArray[5]:
      continue

    value = lineArray[0]

    lowerLeft = lineArray[2].split(',')
    lowerRight = lineArray[3].split(',')
    upperRight = lineArray[4].split(',')
    upperLeft = lineArray[5].split(',')

    if len(lowerLeft) != 2 or len(lowerRight) !=2 or len(upperRight) != 2 or len(upperLeft) != 2:
      continue

    #Get the mid point of the bound where the text matches
    xMean = (int(lowerLeft[0]) + int(lowerRight[0]))/2
    yMean = (int(lowerLeft[1]) + int(upperLeft[1]))/2

    if startingText == "auto":
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


    if endingText == "auto":
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
    dataDictionaryArray.append(cellItem(value, xMean, yMean, lowerLeft[0], lowerLeft[1], (float(lowerRight[0]) - float(lowerLeft[0])), (float(upperLeft[1]) - float(lowerLeft[1])), 0, 0, index + 1))

  xWidthTotal = xWidthTotal/len(dataDictionaryArray)
  startingText = autoStartingText
  endingText = autoEndingText
  testingNumbersFile.close()

def buildReducedArray():
  global endingText
  tempDictionaryArray = []
  global xInterval
  global yInterval
  global dataDictionaryArray
  global columnHandler
  maxWidth = 0
  maxHeight = 0

  #Ignore the texts that lie to the left and top of the threshold text. This improves accuracy of output
  print("Starting text: {} ... Ending text: {}".format(startingText, endingText))
  xLimit = columnHandler.getNearestLineToTheLeft(xStartThreshold) if houghTransform == True else xStartThreshold - 20
  for cell in dataDictionaryArray:
    if cell.y < yStartThreshold - 10 or (xLimit is not None and cell.x < xLimit):
      continue

    if len(endingText) != 0 and (cell.y > yEndThreshold + 10): # or cell.x < xEndThreshold - 30):
      continue

    tempDictionaryArray.append(cell)
    maxWidth = cell.w if cell.w > maxWidth else maxWidth
    maxHeight = cell.h if cell.h > maxHeight else maxHeight

  xInterval = maxWidth/2
  yInterval = maxHeight/2

  dataDictionaryArray = tempDictionaryArray

def assignRowsAndColumns():
  global yInterval
  global xInterval
  global configyInterval
  global configxInterval


  if configxInterval != 0:
    xInterval = configxInterval
  if configyInterval != 0:
    yInterval = configyInterval

  print("Using computed yInterval: {}, xInterval: {}".format(yInterval, xInterval))
  for rowIndex, currentCell in enumerate(dataDictionaryArray):

    if currentCell.row == 0:
      currentCell.row = rowIndex + 1
    for colIndex, restOfTheCells in enumerate(dataDictionaryArray):

      if currentCell.col == 0:
        if houghTransform == True:
          currentCell.col = columnHandler.getColumnNumber(currentCell)
        else:
          currentCell.col = rowIndex + 1

      if restOfTheCells.index == currentCell.index:
        continue

      yUpperBound = currentCell.y + yInterval
      yLowerBound = currentCell.y - yInterval
#If the y coordinate matches, the texts lie on the same row
      if restOfTheCells.row == 0:
        if yLowerBound <= restOfTheCells.y <= yUpperBound:
          restOfTheCells.row = rowIndex + 1

      xUpperBound = currentCell.x + xInterval
      xLowerBound = currentCell.x - xInterval

#If the x coordinate matches, the texts lie on the same column
      if restOfTheCells.col == 0:
        if houghTransform == True:
          restOfTheCells.col = columnHandler.getColumnNumber(restOfTheCells)
        elif xLowerBound <= restOfTheCells.x <= xUpperBound:
          restOfTheCells.col = currentCell.col


def buildTranslationDictionary(startingText, endingText, translationFile):
  '''
  :param: `startingText` <str> - start_key as mentioned in the states.yaml file
  :param: `endingText`   <str> - end_key as mentioned in the states.yaml file
  :param: `translationFile` <os.path> - path to the `<state_code>_districts.meta` file]

  :returns: <dict> - a dictionary containig the text and it's translated value
  '''

  translation_dict = {}

  try:
    with open(translationFile, 'r') as metaFile:
      for line in metaFile:
        if line.startswith('#'):
          continue
        lineArray = line.strip().split(',')
        if len(startingText) != 0:
          if startingText.strip() == lineArray[1].strip():
            startingText = startingText + ',' + lineArray[0].strip()

        if len(endingText) != 0:
          if endingText.strip() == lineArray[1].strip():
            endingText = endingText + ',' + lineArray[0].strip()

        translation_dict[lineArray[0].strip()] = lineArray[1].strip()
  except:
    pass

  return translation_dict


def printOutput(translationDictionary):
  outputFile = open(OUTPUT_TXT, 'w')
  global enableTranslation
  xArray = []
  yArray = []

  image = np.array(Image.open(fileName), dtype=np.uint8)
  fig, ax = plt.subplots(1)
  if houghTransform == True:
    for point in columnHandler.pointList:
      if columnHandler.getNearestLineToTheLeft(xStartThreshold) - 5 <= point.x <= columnHandler.getNearestLineToTheLeft(xStartThreshold) + 5:
        circ = Circle((point.x,point.y),5, color='r')
      else:
        circ = Circle((point.x,point.y),4)
      ax.add_patch(circ)

  for i in range(0, len(dataDictionaryArray)):
    outputString = []
    for cell in dataDictionaryArray:
      if cell.row == i:
        outputString.append(cell)
    outputString.sort(key=lambda x: x.x)

    output = ""
    previousCol = -999
    mergedValue = ""
#<TODO> column verification has to come in here
#Merge those texts separated by spaces - these have the same column value due to proximity but belong to different objects
    columnList = ""
    for index, value in enumerate(outputString):
      value.value = re.sub("\.", "", re.sub(",", "", value.value))
      if index == 0:
        mergedValue = value.value
        previousCol = value.col
        columnList = str(value.col)
        rect = patches.Rectangle((int(value.lbx), int(value.lby)), value.w, value.h,linewidth=0.75,edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        continue

      if value.col == previousCol and is_number(value.value) == False:
        mergedValue = mergedValue + " " + value.value if len(mergedValue) != 0 else value.value
        if index == len(outputString) - 1:
          output += mergedValue if len(output) == 0 else " , " + mergedValue
      else:
        if index == len(outputString) - 1:
          mergedValue = mergedValue + ", " + value.value if len(mergedValue) != 0 else value.value
        output += mergedValue if len(output) == 0 else " , " + mergedValue
        previousCol = value.col
        mergedValue = value.value #+ " ---- " + str(value.col)
        columnList = columnList + ", " + str(value.col) if len(columnList) != 0 else str(value.col)
        rect = patches.Rectangle((int(value.lbx), int(value.lby)), value.w, value.h,linewidth=0.75,edgecolor='r', facecolor='none')
        ax.add_patch(rect)

    if len(output) > 0:
      if enableTranslation == False:
        print("{} | {}".format(output, columnList), file = outputFile)
      else:
        outputArray = output.split(',')
        districtIndex = 0
#If the rows are not numberd, this condition can be skipped. For UP bulletin, this makes sense.
        if(is_number(outputArray[0])):
          districtName = outputArray[1].strip().capitalize()
          distrinctIndex = 1
        else:
          districtName = outputArray[0].strip().capitalize()
          distrinctIndex = 0

#Do a lookup for district name, if not found, discard the record and print a message.
        try:
          translatedValue = translationDictionary[districtName]
          outputString = translatedValue
          for index, value in enumerate(outputArray):
            if index > districtIndex: #and is_number(value):
              outputString += "," + value.strip()
        except KeyError:
          try:
            fuzzyDistrict = fuzzyLookup(translationDictionary,districtName)
            translatedValue = translationDictionary[fuzzyDistrict]
          except:
            print('-------------------------------------------------------------')
            print(f"\n====>>Failed to find lookup for {districtName}\n")
            print('-------------------------------------------------------------')
            continue

        outputString = translatedValue
        for index, value in enumerate(outputArray):
          if index > districtIndex:
            outputString += "," + value.strip()
        print("{} | {}".format(outputString, columnList), file = outputFile)

  outputFile.close()
  ax.imshow(image)
  plt.savefig(OUTPUT_PNG, dpi=300)
  #plt.show()


def fuzzyLookup(translationDictionary,districtName):
  '''
  Use fuzzy string match to map incorrect districtnames
  to the ones in the dictionary
  '''
  from fuzzywuzzy import process
  # Score cut-off of 90 seem to be working well for UP
  district = process.extractOne(
    districtName,
    translationDictionary.keys(),
    score_cutoff = 90)[0]
  print(f"WARN : {districtName} mapped to {district} using Fuzzy Lookup")
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
  ocr_vision.generate(opt['url'])

  global startingText
  global endingText
  global enableTranslation
  global houghTransform
  global fileName
  global translationFile
  global configyInterval
  global configxInterval
  global configMinLineLength

  # set global variables
  start_end_keys        = get_start_end_keys(opt)
  startingText          = start_end_keys['start_key']
  endingText            = start_end_keys['end_key']

  houghTransform        = get_hough_transform(opt)

  enableTranslation     = True
  translationFile       = get_translation_file(opt)

  xy_interval           = get_xy_interval(opt)
  configxInterval       = xy_interval['x']
  configyInterval       = xy_interval['y']

  configMinLineLength   = get_min_line_length(opt)

  fileName              = opt['url']
  config_file           = '_outputs/ocrconfig.meta'


  ## ✅ dependencies removed
  translationDictionary = buildTranslationDictionary(start_end_keys['start_key'], start_end_keys['end_key'], get_translation_file(opt))


  buildCells(translationDictionary, start_end_keys['start_key'], start_end_keys['end_key'])

  # -------


  if houghTransform == True:
    print("Using houghTransform to figure out columns. Set houghTransform:False in ocrconfig.meta.orig to disable this")
    detectLines()

  if len(startingText) != 0 or len(endingText) != 0:
    buildReducedArray()

  assignRowsAndColumns()

  printOutput(translationDictionary)

if __name__ == '__main__':
  sample_opt = {'name': 'Chhattisgarh', 'state_code': 'CT', 'cowin_code': 7, 'url_sources': ['https://twitter.com/HealthCgGov', 'http://cghealth.nic.in/cghealth17/'], 'type': 'image', 'url': '_inputs/ct.jpeg', 'config': {'translation': True}, 'skip_output': False, 'verbose': False}
  run_for_ocr(sample_opt)
