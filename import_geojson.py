from urllib.request import urlopen
import json

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

with open('geojson-counties-fips.json', 'w') as f:
	json.dump(counties, f, indent=4)
