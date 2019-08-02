import ee
ee.Initialize()
year = 2018
year_start = 1985

asset_desti = "projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA4-FT/"
image_source = ee.Image("users/dyedenm/mapbiomas/INFRAURBANA4-FT/infraurbana_v3")
cartas = ee.FeatureCollection("projects/mapbiomas-workspace/AUXILIAR/cartas")
region = cartas.union().geometry().getInfo()['coordinates']

##---------------------------------------------------------------
def export_image(image, name):


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
    image = image_source.select(["classification_" + str(year)])
    export_image(image, str(year))
    
    year -= 1