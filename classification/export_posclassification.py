import ee
ee.Initialize()

import posclassification_lib as posclass_lib
import classification_lib as class_lib

cartas_col = ee.FeatureCollection('projects/mapbiomas-workspace/AUXILIAR/cartas')



# grid_name = 'SD-24-X-A'

def get_image_carta(image, grid_name):

    carta = ee.Feature(cartas_col.filterMetadata('grid_name', 'equals', grid_name).first())
    geometry = carta.geometry().buffer(200)

    image = image.clip(geometry)

    #filter spatial
    image_spatial = posclass_lib.applySpatialFilter(image)


    return posclass_lib.reclassImage(image, image_spatial).clip(geometry)

grid_list = class_lib.getCartasList()

years = [1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 
        1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 
        2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]

grid_processed = [
"SA-19-X-B",  "SA-19-X-D",  "SA-19-Z-A",  "SA-19-Z-B",  "SA-19-Z-C",  "SA-19-Z-D",  "SA-23-Z-A",  "SA-23-Z-B",  "SA-23-Z-C",  
"SA-23-Z-D",  "SA-24-Y-A",  "SA-24-Y-C",  "SB-19-X-B",  "SB-19-Z-A",  "SB-19-Z-D",  "SB-20-Y-C",  "SB-22-X-D",  "SB-22-Z-B",  
"SB-22-Z-D",  "SB-23-V-B",  "SB-23-V-C",  "SB-23-V-D",  "SB-23-X-A",  "SB-23-X-B",  "SB-23-X-C",  "SB-23-X-D",  "SB-23-Y-A",  
"SB-23-Y-B",  "SB-23-Y-C",  "SB-23-Y-D",  "SB-23-Z-A",  "SB-23-Z-B",  "SB-23-Z-C",  "SB-23-Z-D",  "SB-25-V-C",  "SB-25-Y-A",  "SB-25-Y-C", 
"SC-19-X-B",  "SC-19-X-C",  "SC-19-X-D",  "SC-19-Z-A",  "SC-19-Z-B",  "SC-19-Z-C",  "SC-20-V-C",  "SC-20-Y-A",  "SC-20-Y-C",  "SC-21-Y-C", 
"SC-21-Y-D",  "SC-22-V-D",  "SC-22-X-A",  "SC-22-X-B",  "SC-22-X-C",  "SC-22-X-D",  "SC-22-Y-B",  "SC-22-Y-D",  "SC-22-Z-A",  "SC-22-Z-B",
"SC-22-Z-C",  "SC-22-Z-D",  "SC-23-V-A",  "SC-23-V-B",  "SC-23-V-C",  "SC-23-V-D",  "SC-23-X-A",  "SC-23-X-B",  "SC-23-X-C",  "SC-23-X-D",  
"SC-23-Y-A",  "SC-23-Y-B",  "SC-23-Y-C",  "SC-23-Y-D",  "SC-23-Z-A",  "SC-23-Z-B",  "SC-23-Z-C",  "SC-23-Z-D",  "SC-24-X-B",  "SC-24-X-D",  
"SC-24-Y-D",  "SC-24-Z-A",  "SC-24-Z-B",  "SC-24-Z-C",  "SC-24-Z-D",  "SC-25-V-A",  "SC-25-V-C",  "SD-20-X-B",  "SD-21-V-A",  "SD-21-V-B",  
"SD-21-V-C",  "SD-21-V-D",  "SD-21-X-A",  "SD-21-X-B",  "SD-21-X-C",  "SD-21-X-D",  "SD-21-Y-A",  "SD-21-Y-B",  "SD-21-Y-C",  "SD-21-Y-D",  
"SD-21-Z-A",  "SD-21-Z-B",  "SD-21-Z-C",  "SD-21-Z-D",  "SD-22-V-B",  "SD-22-V-C",  "SD-22-V-D",  "SD-22-X-A",  "SD-22-X-B",  "SD-22-X-C",  
"SD-22-X-D",  "SD-22-Y-A",  "SD-22-Y-B",  "SD-22-Y-C",  "SD-22-Y-D",  "SD-22-Z-A",  "SD-22-Z-B",  "SD-22-Z-C",  "SD-22-Z-D",  "SD-23-V-A",  
"SD-23-V-B",  "SD-23-V-C",  "SD-23-V-D",  "SD-23-X-A",  "SD-23-X-B",  "SD-23-X-C",  "SD-23-X-D",  "SD-23-Y-A",  "SD-23-Y-B",  "SD-23-Y-C",  
"SD-23-Y-D",  "SD-23-Z-A",  "SD-23-Z-B",  "SD-23-Z-C",  "SD-23-Z-D",  "SD-24-V-B",  "SD-24-V-C",  "SD-24-V-D",  "SD-24-X-A",  "SD-24-X-C",  
"SD-24-Y-A",  "SD-24-Y-B",  "SD-24-Y-C",  "SD-24-Y-D",  "SD-24-Z-A",  "SD-24-Z-C",  "SE-21-V-A",  "SE-21-V-B",  "SE-21-X-A",  "SE-21-X-B",  
"SE-21-X-D",  "SE-21-Y-B",  "SE-21-Y-D",  "SE-21-Z-A",  "SE-21-Z-B",  "SE-21-Z-C",  "SE-21-Z-D",  "SE-22-V-A",  "SE-22-V-B",  "SE-22-V-C",  
"SE-22-V-D",  "SE-22-X-A",  "SE-22-X-B",  "SE-22-X-C",  "SE-22-X-D",  "SE-22-Y-A",  "SE-22-Y-B",  "SE-22-Y-C",  "SE-22-Y-D",  "SE-22-Z-A",  
"SE-22-Z-B",  "SE-22-Z-C",  "SE-22-Z-D",  "SE-23-X-B",  "SE-23-X-D",  "SE-23-Y-A",  "SE-23-Y-D",  "SE-23-Z-A",  "SE-23-Z-B",  "SE-23-Z-C",  
"SE-23-Z-D",  "SE-24-V-A",  "SE-24-V-B",  "SE-24-V-C",  "SE-24-V-D",  "SE-24-X-A",  "SE-24-Y-A",  "SE-24-Y-B",  "SE-24-Y-C",  "SE-24-Y-D",  
"SF-21-V-B",  "SF-21-V-D",  "SF-21-X-A",  "SF-21-X-D",  "SF-21-Y-B",  "SF-21-Z-A",  "SF-21-Z-B",  "SF-21-Z-C",  "SF-21-Z-D",  "SF-22-V-B",  
"SF-22-V-C",  "SF-22-V-D",  "SF-22-X-A",  "SF-22-X-B",  "SF-22-X-C",  "SF-22-X-D",  "SF-22-Y-A",  "SF-22-Y-B",  "SF-22-Y-C",  "SF-22-Y-D",  
"SF-22-Z-A",  "SF-22-Z-B",  "SF-22-Z-C",  "SF-22-Z-D",  "SF-23-V-A",  "SF-23-V-B",  "SF-23-V-C",  "SF-23-V-D",  "SF-23-X-A",  "SF-23-X-B",  
"SF-23-X-C",  "SF-23-X-D",  "SF-23-Y-A",  "SF-23-Y-B",  "SF-23-Y-C",  "SF-23-Y-D",  "SF-23-Z-A",  "SF-23-Z-B",  "SF-23-Z-C",  "SF-23-Z-D",  
"SF-24-V-A",  "SF-24-V-B",  "SF-24-V-C",  "SF-24-Y-A",  "SF-24-Y-C",  "SG-21-X-B",  "SG-21-X-D",  "SG-21-Z-D",  "SG-22-V-A",  "SG-22-V-B",  
"SG-22-V-C",  "SG-22-V-D",  "SG-22-X-A",  "SG-22-X-B",  "SG-22-X-C",  "SG-22-X-D",  "SG-22-Y-A",  "SG-22-Y-B",  "SG-22-Y-C",  "SG-22-Y-D",  
"SG-22-Z-A",  "SG-22-Z-B",  "SG-22-Z-C",  "SG-22-Z-D",  "SG-23-V-A",  "SG-23-V-B",  "SG-23-V-C",  "SH-21-X-B",  "SH-21-X-D",  "SH-22-V-A",  
"SH-22-V-B",  "SH-22-V-C",  "SH-22-V-D",  "SH-22-X-A",  "SH-22-X-B",  "SH-22-X-C",  "SH-22-X-D"
]

grid_notprocess = list(set(grid_list) - set(grid_processed))

for grid_name in grid_notprocess:
    print(grid_name)
    image_result = None
    for year in years:
        image = posclass_lib.getImageYear(year)
        if year == 1985:
            image_result = get_image_carta(image, grid_name).rename('classification_1985')
        else:
            image_result = image_result.addBands(get_image_carta(image, grid_name).rename('classification_' + str(year)))

    assetid = 'projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA4/' + grid_name + '-1'

    image_result = image_result.set('grid_name', grid_name)
    image_result = image_result.set('version', 1)

    task = ee.batch.Export.image.toAsset(
        image=image_result,
        scale=30,
        description='urban_' + grid_name,
        assetId=assetid,
        pyramidingPolicy='{".default":"mode"}',
        maxPixels=1e13
    )

    task.start()