import ee
ee.Initialize()
year = 2018
year_start = 1985

asset_desti = "projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA3-FT-FINAL/"
collection = ee.ImageCollection("users/dyedenterras/TRANSVERSAIS/INFRAURBANA")
cartas = ee.FeatureCollection("projects/mapbiomas-workspace/AUXILIAR/cartas")
region = cartas.union().geometry().getInfo()['coordinates']

##---------------------------------------------------------------
def export_image(image, name):

    asset_export = asset_desti

    image = image.where(image.neq(1), 27)
    image = image.where(image.eq(1), 24)
    

    task = ee.batch.Export.image.toAsset(
        image = image.toByte(),
        description = "infraurbana_" + name, 
        assetId = asset_desti  + name,
        region = region,
        scale = 30,
        pyramidingPolicy = '{".default":"mode"}',
        maxPixels = 1e13
    )

    task.start()

    print(task.status())

##---------------------------------------------------------------

while year >= year_start:
    print(year)
    image = collection.mosaic().select(["classification_" + str(year)])
    export_image(image, str(year))
    
    year -= 1