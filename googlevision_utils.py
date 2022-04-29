class ColumnHandler:

  def __init__(self):
    self.columnList = []
    self.rowList = []
    self.pointList = []

  def addPoint(self, x, y):
    self.pointList.append({
      'x': x,
      'y': y
    })

  def prepareRow(self):
    rowNumber = 1
    self.pointList.sort(key=lambda y: y['y'])
    for index, col in enumerate(self.pointList):
      if index % 2 == 1:
        continue
      if index == 0:
        previousX = col['x']
        previousY = col['y']
        continue

      if col['y'] - previousY < 10:
        continue
      self.rowList.append({
        'x1': previousX,
        'y1': previousY,
        'x2': col['x'],
        'y2': col['y'],
        'number': rowNumber
      })
      previousX = col['x']
      previousY = col['y']
      rowNumber += 1

  def prepareColumn(self):
    columnNumber = 1
    self.pointList.sort(key=lambda x: x['x'])
    for index, col in enumerate(self.pointList):
      if index % 2 == 1:
        continue
      if index == 0:
        previousX = col['x']
        previousY = col['y']
        continue

      if col['x'] - previousX < 5:
        continue
      self.columnList.append({
        'x1': previousX,
        'y1': previousY,
        'x2': col['x'],
        'y2': col['y'],
        'number': columnNumber
      })
      previousX = col['x']
      previousY = col['y']
      columnNumber += 1

  def printColumnsAndRows(self):
    print('Column No ... x1,y1 --> x2,y2')
    for column in self.columnList:
      print('c{} ... {},{} --> {},{}'.format(column['number'], column['x1'], column['y1'], column['x2'], column['y2']))
    for row in self.rowList:
      print('r{} ... {},{} --> {},{}'.format(row['number'], row['x1'], row['y1'], row['x2'], row['y2']))

  def getNearestLineToTheLeft(self, xCoordinate):
    for col in self.columnList:
      if xCoordinate > int(col['x1']) and xCoordinate < int(col['x2']):
        return col['x1']
    return 0

  def getColumnNumber(self, cell):
    for col in self.columnList:
      if cell['x'] > col['x1'] and cell['x'] < col['x2']:
        return col['number']