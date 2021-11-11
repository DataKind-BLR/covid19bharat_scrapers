import os

def run_for_ocr(opt):
  translation = False
  start_key = 'auto'
  end_key = 'auto'
  if 'config' in opt:
    translation = False if not opt['config']['translation'] else opt['config']['translation']
    if 'start_key' in opt['config']:
      start_key = opt['config']['start_key']
    if 'end_key' in opt['config']:
      end_key = opt['config']['end_key']

  ## step 1 - run something to generate the poly.txt file
  print('Running ocr_vision.py file to generate _outputs/poly.txt')
  os.system('python ocr_vision.py {} > _outputs/bounds.txt'.format(opt['url']))

  ## step 2 - generate ocrconfig.meta file for that state (this overwrites previous file)
  print('Generating ocrconfig.meta file for {}'.format(opt['state_code']))
  os.system('bash generate_ocrconfig.sh {} {} {}'.format(
    opt['state_code'].lower(),
    "{},{}".format(start_key, end_key),
    translation
  ))
  ## step 3 - run googlevision.py file
  print('running googlevision.py using ocrconfig.meta file for {}'.format(opt['state_code']))
  os.system('python googlevision.py _outputs/ocrconfig.meta {}'.format(opt['url']))
