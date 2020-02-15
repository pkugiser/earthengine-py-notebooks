'''
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/ImageCollection/map_function.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/ImageCollection/map_function.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://mybinder.org/v2/gh/giswqs/earthengine-py-notebooks/master?filepath=ImageCollection/map_function.ipynb"><img width=58px src="https://mybinder.org/static/images/logo_social.png" />Run in binder</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/ImageCollection/map_function.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
</table>
'''

# %%
'''
## Install Earth Engine API
Install the [Earth Engine Python API](https://developers.google.com/earth-engine/python_install) and [geehydro](https://github.com/giswqs/geehydro). The **geehydro** Python package builds on the [folium](https://github.com/python-visualization/folium) package and implements several methods for displaying Earth Engine data layers, such as `Map.addLayer()`, `Map.setCenter()`, `Map.centerObject()`, and `Map.setOptions()`.
The following script checks if the geehydro package has been installed. If not, it will install geehydro, which automatically install its dependencies, including earthengine-api and folium.
'''


# %%
import subprocess

try:
    import geehydro
except ImportError:
    print('geehydro package not installed. Installing ...')
    subprocess.check_call(["python", '-m', 'pip', 'install', 'geehydro'])

# %%
'''
Import libraries
'''


# %%
import ee
import folium
import geehydro

# %%
'''
Authenticate and initialize Earth Engine API. You only need to authenticate the Earth Engine API once. 
'''


# %%
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# %%
'''
## Create an interactive map 
This step creates an interactive map using [folium](https://github.com/python-visualization/folium). The default basemap is the OpenStreetMap. Additional basemaps can be added using the `Map.setOptions()` function. 
The optional basemaps can be `ROADMAP`, `SATELLITE`, `HYBRID`, `TERRAIN`, or `ESRI`.
'''

# %%
Map = folium.Map(location=[40, -100], zoom_start=4)
Map.setOptions('HYBRID')

# %%
'''
## Add Earth Engine Python script 

'''

# %%
# This function adds a band representing the image timestamp.
def addTime(image): 
  return image.addBands(image.metadata('system:time_start'))

def conditional(image):
  return ee.Algorithms.If(ee.Number(image.get('SUN_ELEVATION')).gt(40),
                            image,
                            ee.Image(0))

# Load a Landsat 8 collection for a single path-row.
collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA') \
  .filter(ee.Filter.eq('WRS_PATH', 44)) \
  .filter(ee.Filter.eq('WRS_ROW', 34))



# Map the function over the collection and display the result.
print(collection.map(addTime).getInfo())


# Load a Landsat 8 collection for a single path-row.
collection = ee.ImageCollection('LANDSAT/LC8_L1T_TOA') \
  .filter(ee.Filter.eq('WRS_PATH', 44)) \
  .filter(ee.Filter.eq('WRS_ROW', 34))

# This function uses a conditional statement to return the image if
# the solar elevation > 40 degrees.  Otherwise it returns a zero image.
# conditional = function(image) {
#   return ee.Algorithms.If(ee.Number(image.get('SUN_ELEVATION')).gt(40),
#                           image,
#                           ee.Image(0))
# }

# Map the function over the collection, convert to a List and print the result.
print('Expand this to see the result: ', collection.map(conditional).getInfo())



# %%
'''
## Display Earth Engine data layers 

'''


# %%
Map.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
Map