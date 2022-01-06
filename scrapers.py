'''
All this work because the indian govt can't have one unified single dashboard! sigh!

What does this file do?

Provided the following parameters
- `state_code`: 2 letter upper or lower case state code for which you want to extract data for
- `url`: the url or the file path of the pdf, image or html
- `type`: can be either 1 of the 3  pdf, image or html for the url that you provided above

this file will do the following

1. extracts parameters passed from command line or if not, takes defaults from `states.yaml` file
2. based on the provided `url` and the `type`
...

'''

#!/usr/bin/python3
import os
import yaml
import logging
import argparse

from rich.pretty  import pprint
from rich.console import Console
from rich.table import Table
from statewise_get_data import *
from delta_calculator import DeltaCalculator, state_level_delta

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_outputs')
INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_inputs')
STATES_YAML = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'states.yaml')

console = Console(record=True, force_terminal=False)

def draw_table(data, info):
    table = Table(title=f"{info['name']} data from your current input.", title_justify="left", style="bold")

    table.add_column('district', style='white')
    table.add_column('confirmed', style='red', justify='right')
    table.add_column('recovered', style='green', justify='right')
    table.add_column('deceased', style='grey39', justify='right')

    for row in data:
        table.add_row(
            row['districtName'],
            str(row['confirmed']),
            str(row['recovered']),
            str(row['deceased'])
        )

    console.print(table, justify="left")

# read the config file first
with open(STATES_YAML, 'r') as stream:
    try:
        states_all = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

def fetch_data(st_obj):
    '''
    for a given state object, fetch the details from url

    :state:  object as contained in states.yaml
    {
      name: ...
      state_code: ...
      url: ...
    }
    '''
    logging.info(f"Fetching data for {st_obj}")
    fn_map = {
        'ap': ap_get_data,
        'an': an_get_data,
        'ar': ar_get_data,
        'as': as_get_data,
        'br': br_get_data,
        'ch': ch_get_data,
        'ct': ct_get_data,
        'dd': dd_get_data,
        'dh': dh_get_data,
        'dn': dn_get_data,
        'ga': ga_get_data,
        'gj': gj_get_data,
        'hp': hp_get_data,
        'hr': hr_get_data,
        'jh': jh_get_data,
        'jk': jk_get_data,
        'ka': ka_get_data,
        'kl': kl_get_data,
        'ld': ld_get_data,
        'la': la_get_data,
        'mh': mh_get_data,
        'ml': ml_get_data,
        'mn': mn_get_data,
        'mp': mp_get_data,
        'mz': mz_get_data,
        'nl': nl_get_data,
        'or': or_get_data,
        'pb': pb_get_data,
        'py': py_get_data,
        'rj': rj_get_data,
        'sk': sk_get_data,
        'tn': tn_get_data,
        'tg': tg_get_data,
        'tr': tr_get_data,
        'up': up_get_data,
        'ut': ut_get_data,
        'wb': wb_get_data
    }

    try:
        return fn_map[st_obj['state_code'].lower()](st_obj)
    except KeyError:
        print('no function definition in fn_map for state code {}'.format(st_obj['state_code']))

def run(args):
    '''
    :param: <argparse Namespace> - argparse namespace object with configurations
    '''
    state_code = args.state_code.lower()
    url = args.url
    url_type = args.type
    page = args.page if 'page' in args else None
    skip_output = args.skip_output if 'skip_output' in args else False
    is_verbose = args.verbose if 'verbose' in args else False

    # default update skip_output key value
    states_all[state_code].update({ 'skip_output': skip_output })

    if page is not None:
        states_all[state_code]['config'].update({
            'page': page
        })

    if url_type is not None and url is not None:
        # if there's a url & type provided as args, use that
        states_all[state_code].update({
              'url': url,
              'type': url_type
        })

    # always use default `url` & `type` from yaml file
    live_data = fetch_data(states_all[state_code])
    if is_verbose:
        draw_table(live_data, states_all[state_code])

    if 'lazy' in states_all[state_code]:
        state_level_delta(states_all[state_code]['name'], live_data, console)
    else:
        # TODO - get delta for states
        dc = DeltaCalculator(console)
        delta = dc.get_state_data_from_site(
            states_all[state_code]['name'],
            live_data,
            'full',
            is_verbose
        )

    if delta:
        print(f"Delta processing complete. Written to delta.txt")
    else:
        print(f"Delta unchanged.")

    console.save_text(f'{OUTPUTS_DIR}/{state_code}.txt')
    return delta

if __name__ == '__main__':
    '''
    Example to extract from html dashboard (the url will be taken from states.yaml file by default)
    $python scrapers.py --state_code GJ

    Example to overwrite settings already provided in yaml file:
    $python scrapers.py --state_code AP --type pdf --url 'https://path/to/file.pdf'
    '''
    console = Console(record=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--state_code', type=str, nargs='?', required=True, help=f'provide 2 letter state code. Possible options = {states_all.keys()}')
    parser.add_argument('-t', '--type', type=str, choices=['pdf', 'image', 'html'], help='type of url to be specified [pdf, image, html]')
    parser.add_argument('-u', '--url', type=str, help='url/path to the image or pdf to be parsed')
    parser.add_argument('-p', '--page', type=str, help='page numbers to read in case of PDFs')
    parser.add_argument('-o', '--skip_output', action='store_true', help='when you add this flag, it will not generate or update existing output files. Ideally use this when you manually want to update outputs and re-run statewise function')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose will print out all the details in a tabular format')

    args = parser.parse_args()
    run(args)
