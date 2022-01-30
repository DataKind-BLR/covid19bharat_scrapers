import argparse
from contextlib import redirect_stdout
from datetime import datetime, date
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
      
      skip_output = False  
      output_txt = form.get("output_txt")
      if output_txt:
        with open("_outputs/output.txt","w") as f:
          f.write(output_txt.strip(" ").strip("\n"))
          f.close()
        skip_output = True
          
      args = argparse.Namespace(
        state_code = form.get("state_code"),
        page = form.get("page"),
        skip_output = skip_output,
        type = form.get("type"),
        url = url if form.get("type") in ["pdf","image"] else None,
        verbose = False,
        delta_date = date.today()
      )
      
      f = io.StringIO()
      with redirect_stdout(f):
        result = scrapers.run(vars(args))
      delta = f.getvalue()
      
      output_correction = None
      if result and type(result) is dict and result.get("needs_correction"):
        try:
          with open("_outputs/output.txt") as f:
            output_correction = f.read()
            f.close()
        except:
          pass    
        
      return templates.TemplateResponse('index.html', {
        "request": request, 
        "output": delta, 
        "available_state_codes": available_state_codes,
        "output_correction": output_correction})
    except Exception as e:
      output = traceback.format_exc()
      return templates.TemplateResponse('index.html', {
        "request": request, 
        "output": output, 
        "available_state_codes": available_state_codes,
        "output_correction": None})
  else:
    return templates.TemplateResponse('index.html', {
      "request": request, 
      "output": "", 
      "available_state_codes": available_state_codes,
      "output_correction": None})


async def state_details(request):
  return JSONResponse(states_all.get(request.path_params["state_code"],{}))

app = Starlette(debug=True, routes=[
  Route('/', homepage, methods=["GET", "POST"]),
  Route('/state_details/{state_code}', state_details)
])

if __name__ == "__main__":
  uvicorn.run(app, host='0.0.0.0', port=8005)
