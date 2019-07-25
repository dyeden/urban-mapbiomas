import ee
ee.Initialize()

worldpop_col = ee.ImageCollection('WorldPop/POP')
nighttime_col = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
infraprob = ee.ImageCollection('projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA4-PROB-V2')




def getNighttimeLayer():  

    nighttime_2018 = nighttime_col.filterDate('2018-01-01', '2018-12-31').select(['avg_rad']).median()
    nighttime_2017 = nighttime_col.filterDate('2017-01-01', '2017-12-31').select(['avg_rad']).median()
    nighttime_2016 = nighttime_col.filterDate('2016-01-01', '2016-12-31').select(['avg_rad']).median()

    return ee.ImageCollection([nighttime_2017, nighttime_2018, nighttime_2016]).max().rename('nighttime')


def getInfraProbImage(year):

    return infraprob.filterMetadata('year', 'equals', year).mosaic()


def getImageThreshold(image, worldpop, nighttime):

    low_nightlight = nighttime.gt(2)
    medium_nightlight = nighttime.gt(10)
    high_nightlight = nighttime.gt(40)
    pop_high = worldpop.gt(50)

    image_threshold1 = image.gt(95).multiply(low_nightlight)
    image_threshold2 = image.gt(70).multiply(medium_nightlight)
    image_threshold3 = image.gt(40).multiply(high_nightlight).multiply(pop_high)

    result = ee.ImageCollection([image_threshold1, image_threshold2, image_threshold3]).max()

    return result


def getWorlpopLayer():
    return worldpop_col.filterMetadata('UNadj', 'equals', 'yes').filterDate('2019-01-01','2020-12-31').mosaic()


def getImageYear(year):
    worldpop = getWorlpopLayer()
    nighttime = getNighttimeLayer()
    image = getInfraProbImage(year)
    return getImageThreshold(image, worldpop, nighttime)

def applySpatialFilter(image):
    kernel = ee.Kernel.circle(**{'radius': 1})


    image = image.unmask(0) \
            .focal_max(**{'iterations':1,'kernel': kernel}) \
            .focal_min(**{'iterations':1,'kernel': kernel})
            

    image_pixelcount_inverted = image.remap([0,1], [1,0]) \
                        .selfMask().connectedPixelCount()
    image = image.where(image_pixelcount_inverted.lte(30), 1)


    image = image.focal_min(**{'iterations':1,'kernel': kernel}) \
                .focal_max(**{'iterations':1,'kernel': kernel})
                

    image_pixel_count = image.selfMask().connectedPixelCount()   
    image = image.where(image_pixel_count.lte(20), 0)


    return image

def reclassImage(image_original, image_filtered):
  image_original = image_original.unmask(27)
  image_filtered = image_filtered.remap([0,1], [0,24])
  image = image_filtered.where(image_original.eq(27).And(image_filtered.eq(0)), 27)
  
  return image
  
