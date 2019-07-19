import ee
import landsat_lib
import index_lib
import classification_lib as class_lib

ee.Initialize()

cartas_hex_col = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/vectors/cartas_hex")
cartas_col = ee.FeatureCollection('projects/mapbiomas-workspace/AUXILIAR/cartas')
bands = ['blue', 'bu', 'evi', 'green', 'mndwi', 'ndbi', 'ndvi', 'nir', 'red', 'swir1', 'swir2', 'ui']


year = 2011
year_urban = 2010

samples_noturban = ee.FeatureCollection('projects/mapbiomas-workspace/AMOSTRAS/INFRAURBANA_COL4/samples_noturban_carta/samples_noturban_' + str(year));
samples_urban = ee.FeatureCollection("projects/mapbiomas-workspace/AMOSTRAS/INFRAURBANA_COL4/samples_urban_carta/samples_urban_" + str(year_urban));



def start_export(samples_urban, samples_noturban, grid_name,  year):
    carta = ee.Feature(cartas_col.filterMetadata('grid_name', 'equals', grid_name).first())
    carta_hex = ee.Feature(cartas_hex_col.filterMetadata('grid_name', 'equals', grid_name).first()).buffer(100)

    samples_noturban_grid = samples_noturban.filterBounds(carta.geometry().buffer(500))
    samples_urban_grid = samples_urban.filterBounds(carta.geometry().buffer(500))

    samples = samples_urban_grid.merge(samples_noturban_grid).sort('randomc')

    landsat = landsat_lib.getLandsatYear(carta_hex.geometry(), year)

    landsat = class_lib.landsatAddIndex(landsat)

    classified = class_lib.classifyLandsat(landsat, samples, bands)
    classified = classified.set('grid_name', grid_name).set('year', year).clip(carta_hex)


    assetid = 'projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA4-PROB-V2/URBAN_' + grid_name + '_' + str(year)
    task = ee.batch.Export.image.toAsset(**{
        'image':classified,
        'scale':30,
        'description':'urban_' + grid_name + '_' + str(year),
        'assetId':assetid,
        'pyramidingPolicy':'{".default":"mode"}',
        'maxPixels':1e13}
    )

    task.start()




grid_list = class_lib.getCartasList()

for grid_name in grid_list:
    print(grid_name, year)
    start_export(samples_urban, samples_noturban, grid_name, year)




