'''
Given an image file, generate the co-ordinate points
for wherever there's text

call this file like `python ocr_vision.py http://www.rajswasthya.nic.in/COVID20.JPG`
'''
import os
import io
import sys
import requests
from google.cloud import vision

def detect_text(img_path):
  """Detects text in the file."""
  client = vision.ImageAnnotatorClient()

  # reading image directly from url
  url_response = requests.get(img_path)
  image = vision.Image(content=url_response.content)
  resp = client.document_text_detection(image=image)
  texts = resp.text_annotations

  # creating a file called poly.txt & writing text into it
  with io.open('poly.txt', 'w') as boundsFile:
    print(texts, file = boundsFile)
  boundsFile.close()

# Save output
  # for text in texts:
  #   vertices = (['{},{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
  #   print('{}'.format(text.description), end ="|")
  #   print('bounds|{}'.format('|'.join(vertices)))

  # if resp.error.message:
  #   raise Exception(
  #     '{}\nFor more info on error messages, check: '
  #     'https://cloud.google.com/apis/design/errors'.format(
  #     resp.error.message))

if __name__ == "__main__":
  img = sys.argv[1]
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(os.path.dirname(__file__), "visionapi.json")
  detect_text(img)
