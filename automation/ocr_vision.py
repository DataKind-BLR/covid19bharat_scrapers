import os
import io
import sys
from google.cloud import vision

def detect_text(path):
  """Detects text in the file."""
  client = vision.ImageAnnotatorClient()

  with io.open(path, 'rb') as image_file:
    content = image_file.read()

  image = vision.Image(content=content)

  response = client.document_text_detection(image=image)
  texts = response.text_annotations
  print(texts)
  with io.open('poly.txt', 'w') as boundsFile:
    print(texts, file = boundsFile)
  boundsFile.close()

# Save output
  for text in texts:
    vertices = (['{},{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
    print('{}'.format(text.description), end ="|")
    print('bounds|{}'.format('|'.join(vertices)))

  if response.error.message:
    raise Exception(
      '{}\nFor more info on error messages, check: '
      'https://cloud.google.com/apis/design/errors'.format(
      response.error.message))

if __name__ == "__main__":
  file_path = sys.argv[1]
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../../../visionapi_dk.json"
  detect_text(file_path)
