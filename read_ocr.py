import io
import ocr_vision
import googlevision

from contextlib import redirect_stdout


def run_for_ocr(opt):
    '''
    Runs ocr_vision to generate `poly.txt` and provided the output file, generate
    '''

    ## step 1 - run something to generate the poly.txt file
    print('Running ocr_vision.py file to generate _outputs/poly.txt and _outputs/bounds.txt')
    f = io.StringIO()
    with redirect_stdout(f):
      ocr_vision.run(opt['url'])
    result = f.getvalue()

    # step 2 - copy `poly.txt` into `bounds.txt` TODO: Can be eliminated
    print(result)
    import pdb
    pdb.set_trace()
    with open('_outputs/bounds.txt', 'w') as bounds:
      bounds.write(result)
      bounds.close()

    ## step 3 - run googlevision.py file
    print('running googlevision.py using _outputs/bounds.txt file for {}'.format(opt['state_code']))
    googlevision.main(opt)

