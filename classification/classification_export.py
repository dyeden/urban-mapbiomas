import ee
import landsat_lib
import index_lib
import classification_lib as class_lib

hexagons = ee.FeatureCollection('users/dyedenm/mapbiomas/infraurbana_c4/examples/hexagon_urban_example')
brasil = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/vectors/brasil_500m")

points_1994 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_1994")
points_2002 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2002")
points_2010 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2010")
points_2018 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_urban_2018")
points_notu_2018 = ee.FeatureCollection("users/dyedenm/mapbiomas/infraurbana_c4/samples/points_noturban_2018_less_pts")



