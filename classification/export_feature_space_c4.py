import ee
import landsat_lib
import index_lib
import classification_lib as class_lib

brasil = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/vectors/brasil_500m")

points_1994 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_1994")
points_2002 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2002")
points_2010 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2010")
points_2018 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2018")
points_notu_2018 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_noturban_2018")

landsat = landsat_lib.getLandsatMedian(brasil, '2017-10-01','2019-01-01', 'L8', 60)



landsat = landsat.addBands(index_lib.getNDVI(landsat))
landsat = landsat.addBands(index_lib.getMNDWI(landsat))
landsat = landsat.addBands(index_lib.getEVI(landsat))
landsat = landsat.addBands(index_lib.getNDBI(landsat))
landsat = landsat.addBands(index_lib.getBU(landsat))
landsat = landsat.addBands(index_lib.getUI(landsat))

def exportByBlock(landsat, block_id, points, year):

    print(block_id)
    collection = ee.FeatureCollection(points.filterMetadata("block_id", 'equals', block_id))
    ftc = ee.FeatureCollection(landsat.sampleRegions(**{
        'collection':collection,
        'scale':30,
        'geometries':True
    }))



    assetid = 'projects/mapbiomas-workspace/AMOSTRAS/INFRAURBANA_COL4/samples_block/samples_urban_' + str(year) + '_blk_' + str(block_id)
    task = ee.batch.Export.table.toAsset(**{
        'collection':ftc,
        'description':'export_samples_urban_'  + str(year) + '_blk_' + str(block_id),
        'assetId':assetid}
    )

    task.start()

def exportNotUrban(year):

    landsat = landsat_lib.getLandsatMedian(brasil, str(year) + '-01-01', str(year + 1) + '-01-01', 'L8', 60)


    landsat = landsat.addBands(index_lib.getNDVI(landsat))
    landsat = landsat.addBands(index_lib.getMNDWI(landsat))
    landsat = landsat.addBands(index_lib.getEVI(landsat))
    landsat = landsat.addBands(index_lib.getNDBI(landsat))
    landsat = landsat.addBands(index_lib.getBU(landsat))
    landsat = landsat.addBands(index_lib.getUI(landsat))
    
    ftc = ee.FeatureCollection(landsat.sampleRegions(**{
        'collection':points_notu_2018,
        'scale':30,
        'geometries':True
    }))



    assetid = 'projects/mapbiomas-workspace/AMOSTRAS/INFRAURBANA_COL4/samples_notu/samples_noturban_' + str(year)
    task = ee.batch.Export.table.toAsset(**{
        'collection':ftc,
        'description':'export_samples_noturban_'  + str(year) ,
        'assetId':assetid}
    )

    task.start()

# list_year = [1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999]
# list_year = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012]
list_year = [2013, 2014, 2015, 2016, 2017, 2018]
for year in list_year:
    print(year)
    exportNotUrban(year)

# exportByBlock(landsat, 2, points_2002, 2002)


# for block_id in class_lib.getBlocksList():
#         exportByBlock(landsat, block_id, points_2018, 2018)

