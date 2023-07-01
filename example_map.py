import pandas as pd
import json
import numpy as np
from shapely import geometry
import geopy.distance

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})

import plotly.express as px


with open('geojson-counties-fips.json', 'r') as f:
	counties = json.load(f)

def calc_distance(coords_1, coords_2):
	"""
	coords_1 = (52.2296756, 21.0122287)
	coords_2 = (52.406374, 16.9251681)
	"""
	return geopy.distance.geodesic(coords_1, coords_2).miles

class Region(object):
	def __init__(self, coordinates): 
		self.coordinates = coordinates
		self.create_polygon()
		self.get_polygon_centroid()
	
	def create_polygon(self):
		while len(self.coordinates) == 1:
			self.coordinates = self.coordinates[0]

		self.polygon = geometry.Polygon(self.coordinates)
	
	def get_polygon_centroid(self):
		pt = self.polygon.centroid
		self.centroid = (pt.y, pt.x)

class Attributes(object):
	def __init__(self, region):
		self.region = region
		self.metrics = {}
		custom_functions = [m for m in dir(self) if type(getattr(self, m)).__name__ == 'method' and not m=='__init__']
		for function in custom_functions:
			self.metrics[function] = getattr(self, function)()

	def distance_from_logan(self):
		coords1 = (42.3656, -71.0022)
		coords2 = self.region.centroid
		return calc_distance(coords1, coords2)

	def distance_from_nearest_hospital(self):
		hospitals = {
			'Baystate': (42.121522, -72.603006),
			'Yale New Haven': (41.3038, -72.9357),
			'Hartford': (41.7525, -72.6802),
		}
		distances = []
		for hospital_name in hospitals.keys():
			coords1 = hospitals[hospital_name]
			coords2 = self.region.centroid
			d = calc_distance(coords1, coords2)
			distances.append((d, hospital_name))
		distances = sorted(distances)[0]
		
		return distances[0]#], distances[1]


#Filter out only New England States
target_states = ['09', '25', '33', '50', '23', '44']
df['State'] = df['fips'].apply(lambda x: str(x[:2]))
df_sample  = df[df['State'].isin(target_states)]
counties['features'] = [f for f in counties['features'] if f['properties']['STATE'] in target_states]

#Analyze each county
user_data = []
for fip in counties['features']:
	region = Region(fip['geometry']['coordinates'][0])
	attributes = Attributes(region)
	attributes.metrics['id'] = fip['id']
	attributes.metrics['name'] = fip['properties']['NAME']
	user_data.append(attributes.metrics)

user_df = pd.DataFrame.from_dict(user_data)
df_sample = df_sample.set_index('fips').join(user_df.set_index("id")).reset_index()

var = 'distance_from_nearest_hospital'
fig = px.choropleth(df_sample, geojson=counties, locations='fips', color=var,
                           color_continuous_scale="Viridis",
                           range_color=(df_sample[var].min(), df_sample[var].max()),
                           scope="usa",
                           labels={var:var},
                           hover_data = ['name', var]
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
