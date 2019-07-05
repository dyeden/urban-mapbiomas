
def getNDVI(image):

  out = image.expression(
  '(nir - red) / (nir + red )', {
    'nir': image.select('nir'), 
    'red': image.select('red')})

    
  return out.rename('ndvi')
  
def getNDWI(image):

  out = image.expression(
  '(nir - green) / (nir + green )', {
    'nir': image.select('nir'), 
    'green': image.select('green')})    

  return out.rename('ndwi')
 


def getEVI(image):
  
    out = image.expression(
    '2.5 * ((nir - red) / (nir + 6 * red - 7.5 * blue + 1))', {
        'nir': image.select('nir'), 
        'red': image.select('red'), 
        'blue': image.select('blue')
    })

    return out.rename('evi')


def getNDBI(image):

    out = image.expression(
    '(swir1 - nir) / (swir1 + nir)', {
    'swir1': image.select('swir1'), 
    'nir': image.select('nir')})


    return out.rename('ndbi')


def getBU(image):

    out = image.expression(
    'ndbi - ndvi', {
    'ndbi': image.select('ndbi'), 
    'ndvi': image.select('ndvi')})


    return out.rename('bu')

def getUI(image):
  out = image.expression(
  '(swir2 - nir) / (swir2 + nir)', {
    'swir2': image.select('swir2'), 
    'nir': image.select('nir')})
  return out.rename('ui')


def getMNDWI(image):
  out = image.expression(
  '(green - swir1) / (green + swir1)', {
    'swir1': image.select('swir1'), 
    'green': image.select('green')})
  return out.rename('mndwi')
