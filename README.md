# Covid19Bharat Scrapers

### Setup

- If you're using Anaconda to create a virtual environment
```bash
conda env create -f environment.yml
conda activate scraper-covid19bharat
```
- If you're on a flavor of Linux (e.g. Ubuntu) and using virtualenv to create a virtual environment
```bash
virtualenv -p python<pyversion> <path_to_env>/<name_of_environment>
source <path_to_env>/<name_of_environment>/bin/activate
sudo apt-get install  libpoppler-dev libpoppler-cpp-dev
pip install -r linux_requirements.txt
```

---

### Examples For Cases

- To extract from html dashboard (the url will be taken from `states.yaml` file by default)
```bash
$python scrapers.py --state_code GJ
```

- To overwrite settings already provided in `states.yaml` file:
```bash
$python scrapers.py --state_code AP --type pdf --url 'https://path/to/file.pdf'
````

Example to run for images
```bash
python scrapers.py --state_code ML --type image --url '/dir/path/to/ml.jpeg'
```

### Examples For Vaccination Data (Cowin & MoHFW)

Example to extract vaccination data (from Cowin) - at state level with following parameters. The output is written into `_ouputs/vaccination_state_level.csv`
* From 1st Nov 2021
* To 1st Dec 2021
* For states AP, BR and MP only
* At state level from Cowin

```bash
python vaccination.py --source cowin_state --from_date 01-11-2021 --to_date 01-12-2021 --state_code AP,BR,MP
```

Example to extract vaccination data (from Cowin) - at district level.  The output is written into `_ouputs/vaccination_district_level.csv`
When no `from_date` or `to_date` is provided, it will pull for the current date only & for all states since no states are specified
```bash
python vaccination.py --source cowin_district
```

Example to extract vaccination data (from MoHFW) - Works for state level only.  The output is written into `_ouputs/vaccination_mohfw.csv`
```bash
python vaccination.py --source mohfw_state
```

---

## How do the scrapers work?

Everything starts from `states.yaml` file where the configurations, urls and required parameters are added. This is being read by `scrapers.py` file and being executed for each state with the configurations provied. These configurations can be overwritten using the following parameters from the commandline. Based on the necessity of whether it's reading an image or a pdf, one of these 2 files is being called `read_ocr.py` or `read_pdf.py`

- `type` can be one of the three `pdf`, `image` or `html` determines what type of input is being provided to extract data from
- `url` the absolute path or the url of the file type specified in the first parameter
- `state_code` a 2 letter capital state code of the state for which the above paramaters are specified for
- `page` page number incase the url provided is a PDF file
- `skip_output` is a flag mainly used when the OCR or PDF file isn't read correctly by the code. In this case, one can manually modify the output and then re-run using this flag to correctly calculate deltas
- `verbose` to print out detailed output in a tabular format
