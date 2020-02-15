'''
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/Array/spectral_unmixing.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/Array/spectral_unmixing.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://mybinder.org/v2/gh/giswqs/earthengine-py-notebooks/master?filepath=Array/spectral_unmixing.ipynb"><img width=58px src="https://mybinder.org/static/images/logo_social.png" />Run in binder</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/Array/spectral_unmixing.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
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
# Array-based spectral unmixing.

# Create a mosaic of Landsat 5 images from June through September, 2007.
allBandMosaic = ee.ImageCollection('LANDSAT/LT05/C01/T1') \
  .filterDate('2007-06-01', '2007-09-30') \
  .select('B[0-7]') \
  .median()

# Create some representative endmembers computed previously by sampling
# the Landsat 5 mosaic.
urbanEndmember = [88, 42, 48, 38, 86, 115, 59]
vegEndmember = [50, 21, 20, 35, 50, 110, 23]
waterEndmember = [51, 20, 14, 9, 7, 116, 4]

# Compute the 3x7 pseudo inverse.
endmembers = ee.Array([urbanEndmember, vegEndmember, waterEndmember])
inverse = ee.Image(endmembers.matrixPseudoInverse().transpose())

# Convert the bands to a 2D 7x1 array. The toArray() call concatenates
# pixels from each band along the default axis 0 into a 1D vector per
# pixel, and the toArray(1) call concatenates each band (in this case
# just the one band of 1D vectors) along axis 1, forming a 2D array.
inputValues = allBandMosaic.toArray().toArray(1)

# Matrix multiply the pseudo inverse of the endmembers by the pixels to
# get a 3x1 set of endmembers fractions from 0 to 1.
unmixed = inverse.matrixMultiply(inputValues)

# Create and show a colored image of the endmember fractions. Since we know
# the result has size 3x1, project down to 1D vectors at each pixel (since the
# second axis is pointless now), and then flatten back to a regular scalar
# image.
colored = unmixed \
  .arrayProject([0]) \
  .arrayFlatten([['urban', 'veg', 'water']])
Map.setCenter(-98.4, 19, 11)

# Load a hillshade to use as a backdrop.
Map.addLayer(ee.Algorithms.Terrain(ee.Image('CGIAR/SRTM90_V4')).select('hillshade'))
Map.addLayer(colored, {'min': 0, 'max': 1},
  'Unmixed (red=urban, green=veg, blue=water)')


# %%
'''
## Display Earth Engine data layers 

'''


# %%
Map.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
Map