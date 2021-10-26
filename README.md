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

-----

## NOTES

### Step 1

Run the `ocrvision.py` with the below command to generate the `poly.txt` file containing the coordinates for the text
```bash
python ocr_vision.py "path/to/image.jpg"
```

**Dependencies**

- `visionapi.json` -  containing the API key codes


### Step 2

Run the `googlevision.py` parses the coordinates from the `poly.txt` file. This file requires the following dependencies

**Dependencies**

- `poly.txt` - containing the coordinates of the detected text
- `<state_code>_districts.meta` - contains the translation text if it's not in English. This can be skipped if the text on the image are in English. Eg: check `ct_districts.meta` which has Hindi to English translation for district names
- `ocrconfig.meta` - is a generated file from `ocr.sh`,  using the `ocrconfig.meta.orig` as a template

----

Run for states

### West Bengal

```bash
python automation.py "Tamil Nadu" full "pdf=https://stopcorona.tn.gov.in/wp-content/uploads/2020/03/Media-Bulletin-18-10-21-COVID-19.pdf=2"
```

### Karnataka

```bash
python automation.py "Karnataka" full "pdf=https://drive.google.com/file/d/18duJUSus2T0VMt1kC57BGn4LXtQO90_U/view=5"
```

### Tamil Nadu

```bash
python automation.py "Tamil Nadu" full "pdf=https://stopcorona.tn.gov.in/wp-content/uploads/2020/03/Media-Bulletin-18-10-21-COVID-19.pdf=7"
```

### Kerala

```bash
python automation.py "Kerala" full "pdf=https://dhs.kerala.gov.in/wp-content/uploads/2021/10/Bulletin-HFWD-English-October-09-1.pdf=4"
```
