import ee
ee.Initialize()


def renameBandsL57(image):
    image = image.select(['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'sr_atmos_opacity', 'pixel_qa'],
                         ['blue', 'green', 'red', 'nir', 'swir1', 'thermal',
                             'swir2', 'sr_atmos_opacity', 'pixel_qa']
                         )
    out = image.select(['blue', 'green', 'red', 'nir',
                        'swir1', 'swir2']).multiply(0.0001)
    out = out.addBands(image.select(
        ['sr_atmos_opacity', 'thermal', 'pixel_qa']))
    out = out.copyProperties(image).copyProperties(
        image, ['system:time_start'])
    return out


def renameBandsL8(image):
    image = image.select(['B2', 'B3', 'B4', 'B5', 'B6', 'B10', 'B7',  'pixel_qa'],
                         ['blue', 'green', 'red', 'nir', 'swir1',
                             'thermal', 'swir2', 'pixel_qa']
                         )
    out = image.select(['blue', 'green', 'red', 'nir',
                        'swir1', 'swir2']).multiply(0.0001)
    out = out.addBands(image.select(['thermal', 'pixel_qa']))
    out = out.copyProperties(image).copyProperties(
        image, ['system:time_start'])
    return out


def cloudMaskL57(image):
    qa = image.select('pixel_qa')
    atmos = image.select('sr_atmos_opacity')
    cloud = qa.bitwiseAnd(1 << 5) \
        .And(qa.bitwiseAnd(1 << 7)) \
        .Or(qa.bitwiseAnd(1 << 3))

    mask2 = image.mask().reduce(ee.Reducer.min())

    mask3 = qa.bitwiseAnd(1 << 5)

    mask4 = atmos.gt(200)

    return image.updateMask(cloud.Not()).updateMask(mask2).updateMask(mask3.Not()).updateMask(mask4.Not())


def cloudMaskL8(image):
    #   Bits 3 and 5 are cloud shadow and cloud, respectively.
    cloudShadowBitMask = 1 << 3
    cloudsBitMask = 1 << 5

#   Get the pixel QA band.
    qa = image.select('pixel_qa')

#   Both flags should be set to zero, indicating clear conditions.
    mask = qa.bitwiseAnd(cloudShadowBitMask).eq(
        0).And(qa.bitwiseAnd(cloudsBitMask).eq(0))

#   Return the masked image, scaled to TOA reflectance, without the QA bands.
    return image.updateMask(mask).copyProperties(image, ["system:time_start"])


def getGrid(grid_name, buffer):

    cartas = ee.FeatureCollection(
        "projects/mapbiomas-workspace/AUXILIAR/cartas")

    return ee.Feature(cartas.filterMetadata('grid_name', "equals", grid_name).first()).geometry()


def getLandsat5(geometry, date_start, date_end, cloud_cover, tier):

    col = ee.ImageCollection('LANDSAT/LT05/C01/' + tier + '_SR') \
        .filterDate(date_start, date_end) \
        .filterBounds(geometry) \
        .filterMetadata("CLOUD_COVER_LAND", "less_than", cloud_cover)

    col = col.map(renameBandsL57).map(cloudMaskL57).map(
        lambda image: image.clip(geometry))

    return ee.ImageCollection(col)


def getLandsat7(geometry, date_start, date_end, cloud_cover, tier):

    col = ee.ImageCollection('LANDSAT/LE07/C01/' + tier + '_SR') \
            .filterDate(date_start, date_end) \
            .filterBounds(geometry) \
            .filterMetadata("CLOUD_COVER_LAND", "less_than", cloud_cover)

    col = col.map(renameBandsL57).map(cloudMaskL57).map(
        lambda image: image.clip(geometry))

    return ee.ImageCollection(col)


def getLandsat57(geometry, date_start, date_end, cloud_cover, tier):

    col5 = getLandsat5(geometry, date_start, date_end, cloud_cover, tier)

    col7 = getLandsat7(geometry, date_start, date_end, cloud_cover, tier)

    col = col5.merge(col7)

    return ee.ImageCollection(col)


def getLandsat8(geometry, date_start, date_end, cloud_cover, tier):

    col = ee.ImageCollection('LANDSAT/LC08/C01/' + tier + '_SR') \
        .filterDate(date_start, date_end) \
        .filterBounds(geometry) \
        .filterMetadata("CLOUD_COVER_LAND", "less_than", cloud_cover)

    col = col.map(renameBandsL8).map(cloudMaskL8) \
        .map(lambda image: image.clip(geometry))

    return ee.ImageCollection(col)


def getLandsatGeom(geometry, date_start, date_end, sensor, cloud_cover=50, tier='T1'):

    col = None

    if sensor == 'L5':
        col = getLandsat5(geometry, date_start, date_end, cloud_cover, tier)
    elif sensor == 'L7':
        col = getLandsat7(geometry, date_start, date_end, cloud_cover, tier)
    elif sensor == 'L8':
        col = getLandsat8(geometry, date_start, date_end, cloud_cover, tier)
    elif sensor == 'LX':
        col = getLandsat57(geometry, date_start, date_end, cloud_cover, tier)

    return col


def getLandsatMedian(geometry, date_start, date_end, sensor, cloud_cover):
    col = getLandsatGeom(geometry, date_start, date_end, sensor, cloud_cover)
    return col.median().clip(geometry)

def getLandsatYear(geometry, year):
    date_start = str(year) + '-01-01'
    date_end = str(year + 1) + '-01-01'
    sensor = None
    
    if year >= 2013:
        sensor = 'L8'
    elif (year > 1999 and year < 2013):
        sensor = 'LX'
    elif (year < 2000):
        sensor = 'L5'
    
    landsat = getLandsatMedian(geometry, date_start, date_end, sensor, 60)

    return landsat


