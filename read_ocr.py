import ocr_vision
import googlevision

def run_for_ocr(opt):
    ## step 1 - run ocr_vision.py to generate the poly.txt & bounds.txt files
    print('--- Step 1: Running ocr_vision.py file to generate _outputs/poly.txt and _outputs/bounds.txt')
    ocr_vision.generate(opt['url'])

    ## step 2 - run googlevision.py file
    print('--- Step 2: Running googlevision.py using _outputs/bounds.txt file for {}'.format(opt['state_code']))
    googlevision.main(opt)

