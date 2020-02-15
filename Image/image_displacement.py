'''
<table class="ee-notebook-buttons" align="left">
    <td><a target="_blank"  href="https://github.com/giswqs/earthengine-py-notebooks/tree/master/Image/image_displacement.ipynb"><img width=32px src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" /> View source on GitHub</a></td>
    <td><a target="_blank"  href="https://nbviewer.jupyter.org/github/giswqs/earthengine-py-notebooks/blob/master/Image/image_displacement.ipynb"><img width=26px src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/883px-Jupyter_logo.svg.png" />Notebook Viewer</a></td>
    <td><a target="_blank"  href="https://mybinder.org/v2/gh/giswqs/earthengine-py-notebooks/master?filepath=Image/image_displacement.ipynb"><img width=58px src="https://mybinder.org/static/images/logo_social.png" />Run in binder</a></td>
    <td><a target="_blank"  href="https://colab.research.google.com/github/giswqs/earthengine-py-notebooks/blob/master/Image/image_displacement.ipynb"><img src="https://www.tensorflow.org/images/colab_logo_32px.png" /> Run in Google Colab</a></td>
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
import math

# Load the two images to be registered.
image1 = ee.Image('SKYSAT/GEN-A/PUBLIC/ORTHO/MULTISPECTRAL/s01_20150502T082736Z')
image2 = ee.Image('SKYSAT/GEN-A/PUBLIC/ORTHO/MULTISPECTRAL/s01_20150305T081019Z')

# Use bicubic resampling during registration.
image1Orig = image1.resample('bicubic')
image2Orig = image2.resample('bicubic')

# Choose to register using only the 'R' bAnd.
image1RedBAnd = image1Orig.select('R')
image2RedBAnd = image2Orig.select('R')

# Determine the displacement by matching only the 'R' bAnds.
displacement = image2RedBAnd.displacement(**{
  'referenceImage': image1RedBAnd,
  'maxOffset': 50.0,
  'patchWidth': 100.0
})

# Compute image offset And direction.
offset = displacement.select('dx').hypot(displacement.select('dy'))
angle = displacement.select('dx').atan2(displacement.select('dy'))

# Display offset distance And angle.
Map.addLayer(offset, {'min':0, 'max': 20}, 'offset')
Map.addLayer(angle, {'min': -math.pi, 'max': math.pi}, 'angle')
Map.setCenter(37.44,0.58, 15)


# Use the computed displacement to register all Original bAnds.
registered = image2Orig.displace(displacement)

# Show the results of co-registering the images.
visParams = {'bands': ['R', 'G', 'B'], 'max': 4000}
Map.addLayer(image1Orig, visParams, 'Reference')
Map.addLayer(image2Orig, visParams, 'BefOre Registration')
Map.addLayer(registered, visParams, 'After Registration')


alsoRegistered = image2Orig.register(**{
  'referenceImage': image1Orig,
  'maxOffset': 50.0,
  'patchWidth': 100.0
})
Map.addLayer(alsoRegistered, visParams, 'Also Registered')



# %%
'''
## Display Earth Engine data layers 

'''


# %%
Map.setControlVisibility(layerControl=True, fullscreenControl=True, latLngPopup=True)
Map