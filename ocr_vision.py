import os
import io
import sys

from google.cloud import vision


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'visionapi.json'
POLY_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'poly.txt')
BOUNDS_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'bounds.txt')

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


def generate(img_file):
  ## step 1 - generate annotations
  annotations = generate_annotations(img_file)

  ## step 2 - write annotations to `poly.txt`
  with io.open(POLY_TXT, 'w') as poly_file:
    print(annotations, file=poly_file)
  poly_file.close()

  ## step 3 - write annotations again to `bounds.txt` as well
  with io.open(BOUNDS_TXT, 'w') as bounds_file:
    print(annotations, file=bounds_file)
  bounds_file.close()

  ## step 4 - append extracted verticies and description of every line to `bounds.txt`
  '''
    for every annotation, get x & y vertices of annotations and print in following format
                        |  top l   |   top r  | bottom r |  bottom l
    -> `<desc> | bounds | <x>, <y> | <x>, <y> | <x>, <y> | <x>, <y>
  '''
  with io.open(BOUNDS_TXT, 'a') as bounds_file:
    for text in annotations:
      vertices = (['{},{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
      print('{}'.format(text.description), end ='|', file=bounds_file)
      print('bounds|{}'.format('|'.join(vertices)), file=bounds_file)
  bounds_file.close()


if __name__ == '__main__':
  img_file = sys.argv[1]
  generate(img_file)
