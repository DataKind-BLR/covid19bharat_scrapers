#!/usr/bin/python3
import os
import re
import sys
import csv
import yaml
import json
import logging
import camelot
import argparse
import html5lib
import requests
import datetime
import pdftotext

from bs4 import BeautifulSoup
# from deltaCalculator import DeltaCalculator

# read the config file
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "automation.yaml"), "r") as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

def ap_get_data(opt):
  print('fetching AP data', opt)

def ga_get_data(opt):
  print('fetching GA data', opt)

def or_get_data(opt):
  print('fetching OR data', opt)

def rj_get_data(opt):
  print('fetching RJ data', opt)

def mh_get_data(opt):
  print('fetching MH data', opt)

def gj_get_data(opt):
  '''
  This dashboard is not accessible outside India IP
  :return:
  '''
  print('fetching GJ data', opt)

  response = requests.request('GET', opt['url'])
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find('table', {'id': 'tbl'}).find_all('tr')
  districts_data = []

  for row in table[1:]:
    # Ignoring 1st row containing table headers
    d = row.find_all('td')
    districts_data.append({
      'district_name': d[0].get_text(),
      'confirmed': int(d[1].get_text().strip()),
      'recovered': int(d[3].get_text().strip()),
      'deceased': int(d[5].get_text().strip())
    })

  return districts_data
  # TODO = get diff from delta calculator and print it
  # self.delta_calculator.get_state_data_from_site("Gujarat", districts_data, self.option)

def nl_get_data(opt):
  print('fetching NL data', opt)

def mz_get_data(opt):
  print('fetching MZ data', opt)

def as_get_data(opt):
  print('fetching AS data', opt)

def tr_get_data(opt):
  print('fetching TR data', opt)

def py_get_data(opt):
  print('fetching PY data', opt)

def ch_get_data(opt):
  print('fetching CH data', opt)

def kl_get_data(opt):
  print('fetching KL data', opt)

def la_get_data(opt):
  print('fetching LA data', opt)

def ml_get_data(opt):
  print('fetching ML data', opt)


def fetch_data(st_obj):
  '''
  for a given state object, fetch the details from url

  :state:  object as contained in automation.yaml
    {
      name: ...
      state_code: ...
      url: ...
    }
  '''
  fn_map = {
    'ap': ap_get_data,
    'ga': ga_get_data,
    'or': or_get_data,
    'rj': rj_get_data,
    'mh': mh_get_data,
    'gj': gj_get_data,
    'nl': nl_get_data,
    'mz': mz_get_data,
    'as': as_get_data,
    'tr': tr_get_data,
    'py': py_get_data,
    'ch': ch_get_data,
    'kl': kl_get_data,
    'la': la_get_data,
    'ml': ml_get_data
  }

  try:
    fn_map[st_obj['state_code'].lower()](st_obj)
  except KeyError:
    print('no function definition in fn_map for {}'.format(st_obj['name']))


if __name__ == '__main__':
  '''
  $python automation.py
  '''
  parser = argparse.ArgumentParser()
  parser.add_argument('--state_code', type=str, nargs='?', default='all', help='provide 2 letter state code, defaults to all')
  parser.add_argument('--url', type=str, help='url to the ocr image or pdf to be parsed')
  parser.add_argument('--type', type=str, choices=['pdf', 'ocr', 'html'], help='type of url to be specified [pdf, ocr, html]')

  args = parser.parse_args()
  state_code = args.state_code.lower()
  url = args.url
  url_type = args.type

  # execute for all states, if state_code not mentioned
  if state_code == 'all':
    for sc in states_all:
      if states_all[sc]['url']:
        print('running {}_get_data'.format(sc))
        fetch_data(states_all[sc])
  else:
    if url is not None or url_type is not None:
      # if there's a url & type provided as args, use that
      states_all[state_code].update({
        'type': url_type,
        'url': url
      })
      fetch_data(states_all[state_code])
    else:
      # else use default url & type from yaml file
      fetch_data(states_all[state_code])

