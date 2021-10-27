# Covid19Bharat Scrapers

Example to extract from html dashboard (the url will be taken from `states.yaml` file by default)
```bash
$python scrapers.py --state_code GJ
```

Example to overwrite settings already provided in yaml file:
```bash
$python scrapers.py --state_code AP --type pdf --url 'https://path/to/file.pdf'
````

Example to run for images
```bash
python scrapers.py --state_code ML --type image --url '/dir/path/to/ml.jpeg'
```

NOTE: The `--url` parameter can either a direct link over the internet to the file or could be a path in your local directory


## How does this work?

Everything starts from `states.yaml` file where the configurations, urls and required parameters are added. This is being read by `scrapers.py` file and being executed for each state with the configurations provied. These configurations can be overwritten using the following parameters from the commandline

- `type` can be one of the three `pdf`, `image` or `html` determines what type of input is being provided to extract data from
- `url` the absolute path or the url of the file type specified in the first parameter
- `state_code` a 2 letter capital state code of the state for which the above paramaters are specified for
