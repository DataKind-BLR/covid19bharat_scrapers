import os
import sys
import io
import pickle
from google.cloud import vision

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'visionapi.json'
POLY_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'poly.txt')
BOUNDS_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs', 'bounds.txt')

def generate_annotations(img_file):
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


def run(path):
  '''Detects text in the file.'''
  texts = generate_annotations(path)

  ## Whatever is being printed here, is being written into the `bounds.txt` file
  with io.open(POLY_TXT, 'w') as poly_file:
    print(texts, file=poly_file)
  poly_file.close()

  for text in texts:
    vertices = (['{},{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
    print('{}'.format(text.description), end ="|")
    print('bounds|{}'.format('|'.join(vertices)))


if __name__ == '__main__':
  path = sys.argv[1]
  run(path)
