# Covid19Bharat Scrapers

Example to extract from html dashboard (the url will be taken from `automation.yaml` file by default)
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
