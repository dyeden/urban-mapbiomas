import ee
import landsat_lib
import index_lib
import classification_lib as class_lib

ee.Initialize()

bands = ['blue', 'bu', 'evi', 'green', 'mndwi', 'ndbi', 'ndvi', 'nir', 'red', 'swir1', 'swir2', 'ui']

# block_id = 548
YEAR = 2017
YEAR_URBAN = 2018


samples_noturban = class_lib.getSamplesNotUrban(YEAR)


def getLandsatYear(hexagons_block, year):
    date_start = str(year) + '-01-01'
    date_end = str(year + 1) + '-01-01'
    sensor = None
    if year >= 2013:
        sensor = 'L8'
    elif year >= 2000 and year < 2013:
        sensor = 'LX'
    elif year < 2000:
        sensor = 'L5'
    landsat = landsat_lib.getLandsatMedian(hexagons_block, date_start,date_end, sensor, 60)

    landsat_block = class_lib.getLandsantBlock(hexagons_block, landsat)
    landsat_block = landsat_block.map(class_lib.landsatAddIndex)

    return landsat_block



def start_export(block_id, YEAR, YEAR_URBAN):
    hexagons_block = class_lib.getHexagonsBlock(block_id)
    samples_urban_block = class_lib.getSamplesUrbanBlock(block_id, YEAR_URBAN)
    samples_noturban_block = samples_noturban.filterMetadata('block_id', 'equals', block_id)
    samples_block = samples_urban_block.merge(samples_noturban_block)


    urban_hex_list = class_lib.getListHexId(samples_urban_block)
    noturban_hex_list = class_lib.getListHexId(samples_noturban_block)


    hexagons_block = hexagons_block.filter(ee.Filter.inList('hex_id', urban_hex_list))
    hexagons_block = hexagons_block.filter(ee.Filter.inList('hex_id', noturban_hex_list))

 
    landsat_block = getLandsatYear(hexagons_block, YEAR)


    classified = class_lib.classifyBlock(landsat_block, samples_block, bands).toByte()

    assetid = 'projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA4-PROB/urbana_'+ str(YEAR) + '_' + str(block_id)


    region = hexagons_block.geometry().bounds().getInfo()['coordinates']

    task = ee.batch.Export.image.toAsset(**{
        'image':classified,
        'region':region,
        'scale':30,
        'description':'urban_'  + str(YEAR) + '_block_'  + str(block_id),
        'assetId':assetid,
        'pyramidingPolicy':'{".default":"mode"}',
        'maxPixels':1e13}
    )

    task.start()

block_ids_lists = class_lib.getBlocksList()
for block_id in block_ids_lists:
    if block_id == 559:
        print('--------------------------------------------------------------------------')
        print(block_id)          
        start_export(block_id, YEAR, YEAR_URBAN)
        print('OK')


