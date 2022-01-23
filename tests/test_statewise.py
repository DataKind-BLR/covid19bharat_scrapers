import os
import yaml

from statewise_get_data import *


STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'states.yaml')
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_inputs')
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_outputs')


with open(STATES_YAML, 'r') as stream:
    try:
        states_all = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def test_ar():
    opt = states_all['ar']
    states_all['ar']['verbose'] = False
    states_all['ar']['skip_output'] = False
    ar_data = ar_get_data(opt)
    print(ar_data)


test_ar()
