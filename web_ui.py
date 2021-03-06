import io
import os
import re
import uvicorn
import scrapers
import traceback
import vaccination

from datetime import datetime, date
from starlette.routing import Route
from contextlib import redirect_stdout
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates


templates = Jinja2Templates(directory='templates')
states_all = scrapers.states_all

async def write_file(file_obj):
  contents = await file_obj.read()
  save_file_name = datetime.utcnow().isoformat() + '-' + file_obj.filename
  save_file_name = os.path.join(scrapers.INPUTS_DIR, save_file_name)
  with open(save_file_name, 'wb') as f:
    f.write(contents)
    f.close()
  return save_file_name

async def homepage(request):
  available_state_codes = list(states_all.keys())

  if request.method == 'POST':

    try:
      form = await request.form()

      url = None
      if form.get('file'):
        url = await write_file(form['file'])

      skip_output = False
      output_txt = form.get('output_txt')

      if output_txt:
        with open(os.path.join(scrapers.OUTPUTS_DIR, 'output.txt'),'w') as f:
          f.write(output_txt.strip(' ').strip('\n'))
          f.close()
        skip_output = True

      args = {
        'state_code': form.get('state_code'),
        'page': form.get('page'),
        'skip_output': skip_output,
        'type': form.get('type'),
        'url': url if form.get('type') in ['pdf','image'] else None
      }

      f = io.StringIO()
      with redirect_stdout(f):
        result = scrapers.run(args)
      delta = f.getvalue()

      output_correction = None
      if 'needs_correction' in result and result['needs_correction'] == True:
        try:
          with open(os.path.join(scrapers.OUTPUTS_DIR, 'output.txt')) as f:
            output_correction = f.read()
            f.close()
        except:
          pass


      return templates.TemplateResponse('index.html', {
        'request': request,
        'output': delta,
        'available_state_codes': available_state_codes,
        'output_correction': output_correction
      })

    except Exception as e:
      output = traceback.format_exc()
      return templates.TemplateResponse('index.html', {
        'request': request,
        'output': output,
        'available_state_codes': available_state_codes,
        'output_correction': None
      })

  return templates.TemplateResponse('index.html', {
    'request': request,
    'output': '',
    'available_state_codes': available_state_codes,
    'output_correction': None
  })


async def vaccination_route(request):
  output = ''
  f = io.StringIO()
  is_mohfw = False

  with redirect_stdout(f):
    try:
      if request.method=='POST':
        form = await request.form()
        fn_map = {
          'cowin_state': vaccination.get_cowin_state,
          'cowin_district': vaccination.get_cowin_district,
          'mohfw_state': vaccination.get_mohfw_state
        }
        vacc_src = form.get('source').lower()
        is_mohfw = vacc_src=='mohfw_state'

        if os.path.exists('_outputs/vaccination_state_level.txt'):
          os.remove('_outputs/vaccination_state_level.txt')

        if os.path.exists('_outputs/vaccination_district_level.csv'):
          os.remove('_outputs/vaccination_district_level.csv')

        state_codes = None
        if form.get('state_codes'):
          state_codes = list(map(lambda sc: sc.lower().strip(), form.get('state_codes').split(',')))

        from_date = datetime(*list(map(int, form.get('from_date').split('-')))) if form.get('from_date') else datetime.today()

        to_date = datetime(*list(map(int, form.get('to_date').split('-')))) if form.get('to_date') else None
        if to_date is None or to_date <= from_date:
            to_date = from_date

        fn_map[vacc_src](from_date, to_date, state_codes)

        if vacc_src=='cowin_state':
          with open('_outputs/vaccination_state_level.txt') as ff:
            output += ff.read() + '\n'
            ff.close()
        if vacc_src=='cowin_district':
          with open('_outputs/vaccination_district_level.csv') as ff:
            output += ff.read() + '\n'
            ff.close()
    except Exception as e:
      output += traceback.format_exc() + '\n'

  if is_mohfw:
    output = f.getvalue() + '\n' + output
  ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
  return templates.TemplateResponse('vaccination.html', {
    'request': request,
    'output': ansi_escape.sub('', output)})



async def state_details(request):
  return JSONResponse(states_all.get(request.path_params['state_code'],{}))


if __name__ == '__main__':
  app = Starlette(debug=True, routes=[
    Route('/', homepage, methods=['GET', 'POST']),
    Route('/vaccination', vaccination_route, methods=['GET', 'POST']),
    Route('/state_details/{state_code}', state_details)
  ])
  uvicorn.run(app, host='0.0.0.0', port=8005)
