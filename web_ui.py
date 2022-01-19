import argparse
from contextlib import redirect_stdout
from datetime import datetime
import io
import os
from pathlib import Path
import scrapers
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
import traceback
import uvicorn
import yaml

templates = Jinja2Templates(directory='templates')

STATES_YAML_FILE = 'states.yaml'
with open(STATES_YAML_FILE) as stream:
  try:
    states_all = yaml.safe_load(stream)
  except yaml.YAMLError as e:
    print(f"Error in Opening YAML States - {e}")

async def write_file(file_obj):
  Path("web_ui_uploads").mkdir(parents=True, exist_ok=True)
  contents = await file_obj.read()
  save_file_name = datetime.utcnow().isoformat() + "-" + file_obj.filename
  save_file_name = os.path.join("web_ui_uploads", save_file_name)
  with open(save_file_name, "wb") as f:
    f.write(contents)
    f.close()
  return save_file_name  
  
async def homepage(request):
  available_state_codes = list(scrapers.fn_map.keys())
  if request.method=="POST":
    try:
      form = await request.form()
      
      url = None
      if form.get("file"):
        url = await write_file(form["file"])
        
      args = argparse.Namespace(
        state_code = form.get("state_code"),
        page = None,
        skip_output = False,
        type = form.get("type"),
        url = url if form.get("type") in ["pdf","image"] else None,
        verbose = False
      )
      
      f = io.StringIO()
      with redirect_stdout(f):
        scrapers.run(args)
      delta = f.getvalue()
         
      return templates.TemplateResponse('index.html', {"request": request, "output": delta, "available_state_codes": available_state_codes})
    except Exception as e:
      output = traceback.format_exc()
      return templates.TemplateResponse('index.html', {"request": request, "output": output, "available_state_codes": available_state_codes})
  else:
    return templates.TemplateResponse('index.html', {"request": request, "output": "", "available_state_codes": available_state_codes})


async def state_details(request):
  return JSONResponse(states_all.get(request.path_params["state_code"],{}))

app = Starlette(debug=True, routes=[
  Route('/', homepage, methods=["GET", "POST"]),
  Route('/state_details/{state_code}', state_details)
])

if __name__ == "__main__":
  uvicorn.run(app, host='0.0.0.0', port=8005)
