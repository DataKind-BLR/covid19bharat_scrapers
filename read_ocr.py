import os

def run_for_ocr(opt):
  translation = False if not opt['config']['translation'] else True

  ## step 1 - run something to generate the poly.txt file
  print('Running ocr_vision.py file to generate poly.txt')
  os.system('python ocr_vision.py {} > bounds.txt'.format(opt['url']))

  ## step 2 - generate ocrconfig.meta file for that state (this overwrites previous file)
  print('Generating ocrconfig.meta file for {}'.format(opt['state_code']))
  os.system('bash generate_ocrconfig.sh {} {} {}'.format(
    opt['state_code'].lower(),
    "auto,auto",
    translation
  ))
  ## step 3 - run googlevision.py file
  print('running googlevision.py using ocrconfig.meta file for {}'.format(opt['state_code']))
  os.system('python googlevision.py ocrconfig.meta {}'.format(opt['url']))
