'''
TODO

- import parent directory files here

'''
import os

INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_inputs')
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '_outputs')
STATES_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'states_test.yaml')

# read the config file first
with open(STATES_YAML, 'r') as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

def test_sample():
    assert sum([1, 2, 4]) == 6, "Should be 6"

def test_ap():
    opt = states_all['ap']
    print(c19bscrapers.statewise_get_data.ap_get_data(opt))

if __name__ == "__main__":
    # test_sample()
    test_ap()
    print("Everything passed")
