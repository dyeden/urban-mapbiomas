import ee
import landsat_lib
import index_lib
import classification_lib as class_lib

hexagons = ee.FeatureCollection('users/dyedenm/mapbiomas/infraurbana_c4/examples/hexagon_urban_example')

brasil = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/vectors/brasil_500m")

points_1994 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_1994_less")
points_2002 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2002_less")
points_2010 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2010_less")
points_2018 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2018_less")
points_notu_2018 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_noturban_2018_less_pts")


def exportByBlock(block_id, points, year):

    landsat = landsat_lib.getLandsatMedian(brasil, '2017-01-01','2019-06-01', 'L8', 60).clip(hexagons)
    landsat = landsat.addBands(index_lib.getNDVI(landsat))
    landsat = landsat.addBands(index_lib.getMNDWI(landsat))
    landsat = landsat.addBands(index_lib.getEVI(landsat))
    landsat = landsat.addBands(index_lib.getNDBI(landsat))
    landsat = landsat.addBands(index_lib.getBU(landsat))
    landsat = landsat.addBands(index_lib.getUI(landsat))


    collection = ee.FeatureCollection(points.filterMetadata("block_id", 'equals', block_id))
    ftc = ee.FeatureCollection(landsat.sampleRegions(**{
        'collection':collection,
        'scale':30,
        'geometries':True,
        'tileScale':16
    }))



    assetid = 'projects/mapbiomas-workspace/AMOSTRAS/INFRAURBANA_COL4/samples_urban/samples_urban_' + str(year) + '_blk_' + str(block_id)
    task = ee.batch.Export.table.toAsset(**{
        'collection':ftc,
        'description':'export_samples_urban_'  + str(year) + '_blk_' + str(block_id),
        'assetId':assetid}
    )

    task.start()

def exportNotUrban(year, part, points):

    sensor = None
    if year in range(1985, 2000):
        sensor = 'L5'

    if year in range(2000, 2013):
        sensor = 'LX'

    if year in range(2013, 2019):
        sensor = 'L8'


    landsat = landsat_lib.getLandsatMedian(brasil, str(year) + '-01-01', str(year + 1) + '-01-01', sensor, 60)

    landsat = landsat.clip(hexagons)


    landsat = landsat.addBands(index_lib.getNDVI(landsat))
    landsat = landsat.addBands(index_lib.getMNDWI(landsat))
    landsat = landsat.addBands(index_lib.getEVI(landsat))
    landsat = landsat.addBands(index_lib.getNDBI(landsat))
    landsat = landsat.addBands(index_lib.getBU(landsat))
    landsat = landsat.addBands(index_lib.getUI(landsat))
    
    ftc = ee.FeatureCollection(landsat.sampleRegions(**{
        'collection':points,
        'scale':80,
        'geometries':True,
        'tileScale':16
    }))

    assetid = 'projects/mapbiomas-workspace/AMOSTRAS/INFRAURBANA_COL4/samples_notuv2/samples_noturban_' + str(year) + '_part' + str(part)
    task = ee.batch.Export.table.toAsset(**{
        'collection':ftc,
        'description':'export_samples_noturban_'  + str(year) + '_part'  + str(part),
        'assetId':assetid}
    )

    task.start()

list_year_c1 = [1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993]
list_year_c2 = [1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002]
list_year_c3 = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011]
list_year_c4 = [2012, 2013, 2014, 2015, 2016, 2017, 2018]


for part in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
    for year in list_year_c1:
        print([year, part])
        list_block_ids = class_lib.getBlocksListPartV2(part)
        points= ee.FeatureCollection(points_notu_2018.filter(ee.Filter.inList('block_id', ee.List(list_block_ids))))
        exportNotUrban(year, part, points)


# for block_id in class_lib.getBlocksList():
#     print(block_id)
#     exportByBlock( block_id, points_2018, 2018)

