from contextlib import redirect_stdout
import io
import os

import googlevision
import ocr_vision

python_cmd = 'python'
if os.path.exists('use_venv_for_cmd'):
    python_cmd = 'venv/bin/python3'

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
    
    f = io.StringIO()
    with redirect_stdout(f):
      ocr_vision.run(opt["url"])
    result = f.getvalue()
    
    with open("_outputs/bounds.txt", "w") as f:
      f.write(result)
      f.close()  
    
    # os.system('{} ocr_vision.py {} > _outputs/bounds.txt'.format(python_cmd, opt['url']))

    ## step 2 - generate ocrconfig.meta file for that state (this overwrites previous file)
    print('Generating ocrconfig.meta file for {}'.format(opt['state_code']))
    os.system('bash generate_ocrconfig.sh {} {} {}'.format(
        opt['state_code'].lower(),
        '{},{}'.format(start_key, end_key),
        translation
    ))
    
    ## step 3 - run googlevision.py file
    print('running googlevision.py using ocrconfig.meta file for {}'.format(opt['state_code']))
    googlevision.main(config_file="_outputs/ocrconfig.meta", file_name=opt["url"])
    #os.system('{} googlevision.py _outputs/ocrconfig.meta {}'.format(python_cmd, opt['url']))
