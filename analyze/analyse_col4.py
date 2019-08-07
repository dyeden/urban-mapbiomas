import ee
ee.Initialize()

def get_area(asset_imc, geometry, year):
    image = ee.Image( asset_imc + '/' + str(year)).clip(geometry)

    image_area = ee.Image.pixelArea().divide(10000).clip(geometry)
    raw_data = image_area.mask(image.select('classification_' + str(year)).eq(24)).reduceRegion(**{
    'reducer':ee.Reducer.sum(), 
    'geometry':geometry,
    'scale':30
    } )

    return raw_data.get('area')


def get_stats_cobertura_mun(municipio_name, col=4):
    if col == 4:
        asset_imc = 'projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA4-FT'
    elif col == 3:
        asset_imc = 'projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA3-FT-FINAL'
    
    municipios = ee.FeatureCollection('projects/mapbiomas-workspace/AUXILIAR/municipios-2016');
    municipio = ee.Feature(municipios.filterMetadata('NM_MUNICIP', 'equals', municipio_name).first())
    geometry = municipio.geometry()
    area_mun = geometry.area().divide(10000)
    
    years = [1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 
        1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 
        2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
    
    info = []
    
    for year in years:

        area = get_area(asset_imc,  geometry, year)
        info.append(ee.Feature(None, {'year':year, 'area':area, 'name':municipio_name, 'area_mun':area_mun}))
        
    ftc = ee.FeatureCollection(info).getInfo()
    
    
    return [item['properties'] for item in ftc['features']]