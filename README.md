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
### Examples

- To extract from html dashboard (the url will be taken from `states.yaml` file by default)
```bash
$python scrapers.py --state_code GJ
```

- To overwrite settings already provided in yaml file:
```bash
$python scrapers.py --state_code AP --type pdf --url 'https://path/to/file.pdf'
````

Example to run for images
```bash
python scrapers.py --state_code ML --type image --url '/dir/path/to/ml.jpeg'
```

NOTE: The `--url` parameter can either a direct link over the internet to the file or could be a path in your local directory

---
## How does this work?

Everything starts from `states.yaml` file where the configurations, urls and required parameters are added. This is being read by `scrapers.py` file and being executed for each state with the configurations provied. These configurations can be overwritten using the following parameters from the commandline. Based on the necessity of whether it's reading an image or a pdf, one of these 2 files is being called `read_ocr.py` or `read_pdf.py`

- `type` can be one of the three `pdf`, `image` or `html` determines what type of input is being provided to extract data from
- `url` the absolute path or the url of the file type specified in the first parameter
- `state_code` a 2 letter capital state code of the state for which the above paramaters are specified for
