# coding: utf-8
import ee
import csv
import pprint

ee.Initialize()

rule_ft_csv = './regras-filtro-temporal-area-urbana-c4.csv'

cartas = ee.FeatureCollection("projects/mapbiomas-workspace/AUXILIAR/cartas")

params = {

    "asset": {
        "classificacao": "projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA4",
        "classificacaoft": "users/dyedenm/mapbiomas/INFRAURBANA4-FT",
    },

    'bands': [
        'classification_1985',
        'classification_1986',
        'classification_1987',
        'classification_1988',
        'classification_1989',
        'classification_1990',
        'classification_1991',
        'classification_1992',
        'classification_1993',
        'classification_1994',
        'classification_1995',
        'classification_1996',
        'classification_1997',
        'classification_1998',
        'classification_1999',
        'classification_2000',
        'classification_2001',
        'classification_2002',
        'classification_2003',
        'classification_2004',
        'classification_2005',
        'classification_2006',
        'classification_2007',
        'classification_2008',
        'classification_2009',
        'classification_2010',
        'classification_2011',
        'classification_2012',
        'classification_2013',
        'classification_2014',
        'classification_2015',
        'classification_2016',
        'classification_2017',
        'classification_2018'
    ]
}


class TemporalFilter(object):

    options = {

        "asset": {
        },

        "ft_rules": {},

        'bands': []

    }


    def __init__(self, params):

        self.params = params

        self.options.update(params)

        self.loadRules()


    def loadRules(self):

        self.options['ft_rules'] = {
            'rpk3': filter(lambda rule:
                           rule['type'] == 'RP' and rule['kernel'] == 3,
                           self.params['ft_rules']
                           ),
            'rgk3': filter(lambda rule:
                           rule['type'] == 'RG' and rule['kernel'] == 3,
                           self.params['ft_rules']
                           ),
            'ruk3': filter(lambda rule:
                           rule['type'] == 'RU' and rule['kernel'] == 3,
                           self.params['ft_rules']
                           ),
            'rpk5': filter(lambda rule:
                           rule['type'] == 'RP' and rule['kernel'] == 5,
                           self.params['ft_rules']
                           ),
            'rgk5': filter(lambda rule:
                           rule['type'] == 'RG' and rule['kernel'] == 5,
                           self.params['ft_rules']
                           ),
            'ruk5': filter(lambda rule:
                           rule['type'] == 'RU' and rule['kernel'] == 5,
                           self.params['ft_rules']
                           )
        }

    def getClassificacao(self):
        return ee.ImageCollection(self.options['asset']['classificacao']).max()

    
    def noData2NotObserved(self, image):
        """
        Reclassify the no data value to not observed class value
        """
        image = ee.Image(image)


        image = image.where(image.eq(0), 27).copyProperties(image)

        image = ee.Image(image)

        image = image.unmask(27).copyProperties(image) 

        return ee.Image(image)


    def applyRuleKernel3(self, imageList, rule, kernelIds, ruleId):

        exp = "((img1==%s) and (img2==%s) and (img3==%s))" % (
            rule['tminus1'], rule['t'], rule['tplus1'])

        mask = imageList[ruleId].expression(exp, {
            'img1': imageList[kernelIds[0]],
            'img2': imageList[kernelIds[1]],
            'img3': imageList[kernelIds[2]]
        })

        image = imageList[ruleId].where(mask.eq(1), rule['result'])

        return image

    def applyRuleKernel5(self, imageList, rule, kernelIds, ruleId):

        exp = "(img1==%s) and (img2==%s) and (img3==%s) and (img4==%s) and (img5==%s)" % (
            rule['tminus2'], rule['tminus1'], rule['t'], rule['tplus1'], rule['tplus2'])

        mask = imageList[ruleId].expression(exp, {
            'img1': imageList[kernelIds[0]],
            'img2': imageList[kernelIds[1]],
            'img3': imageList[kernelIds[2]],
            'img4': imageList[kernelIds[3]],
            'img5': imageList[kernelIds[4]]
        })

        image = imageList[ruleId].where(mask.eq(1), rule['result'])

        return image

    
    def list2multband(self, imageList):

        image = imageList[0]

        n = len(imageList)

        for band in imageList[1:n]:
            image = image.addBands(band)

        return image

    def applyRulesNotCumulative(self, image):
        imageListOrig = [image.select(band) for band in self.options['bands']]
        imageList = [image.select(band) for band in self.options['bands']]

        n = len(self.options['bands'])

        for i in range(1, n-2):
            for rule in self.options['posft_rules']['ruk3']:
                imageList[i] = self.applyRuleKernel3(
                    imageListOrig,
                    rule,
                    [i-1, i, i+1],
                    i+1
                )

        
        for rule in self.options['ft_rules']['ruk3']:
            imageList[n-1] = self.applyRuleKernel3(
                imageList,
                rule,
                [n-3, n-2, n-1],
                n-1
            )

        filtered = self.list2multband(imageList)

        return filtered


    def applyRules(self, image):        

        imageList = [image.select(band) for band in self.options['bands']]

        imageList = map(self.noData2NotObserved, imageList)
        # imageList = map(self.fillHoles, imageList)

        n = len(self.options['bands'])


        # rules kernel 5
        for rule in self.options['ft_rules']['rpk5']:
            imageList[0] = self.applyRuleKernel5(
                imageList,
                rule,
                [0, 1, 2, 3, 4],
                0
            )

        for i in range(2, n-3):
            for rule in self.options['ft_rules']['rgk5']:
                imageList[i] = self.applyRuleKernel5(
                    imageList,
                    rule,
                    [i-2, i-1, i, i+1, i+2],
                    i
                )
        
        # for rule in self.options['ft_rules']['ruk5']:
        #     imageList[n-1] = self.applyRuleKernel5(
        #         imageList,
        #         rule,
        #         [n-5, n-4, n-3, n-2, n-1],
        #         n-1
        #     )

        # # rules kernel 3
        # for rule in self.options['ft_rules']['rpk3']:
        #     imageList[0] = self.applyRuleKernel3(
        #         imageList,
        #         rule,
        #         [0, 1, 2],
        #         0
        #     )

        # for i in range(1, n-2):
        #     for rule in self.options['ft_rules']['rgk3']:
        #         imageList[i] = self.applyRuleKernel3(
        #             imageList,
        #             rule,
        #             [i-1, i, i+1],
        #             i
        #         )

        # for rule in self.options['ft_rules']['ruk3']:
        #     imageList[n-1] = self.applyRuleKernel3(
        #         imageList,
        #         rule,
        #         [n-3, n-2, n-1],
        #         n-1
        #     )
        
        filtered = self.list2multband(imageList)
        pprint.pprint(filtered.getInfo())
        return filtered

def ImcToImage(imc):


    def map_func(image):
        name = ee.String(image.get('band_name'))
        year = ee.String(name).slice(15) 
        img = image.set('band_name', ee.String('classification_').cat(year)) \
                    .set('year',year) \
                    .set('system:time_start', year.cat(ee.String('-01-01'))) \
                    .rename('classification') 
        return img



    imc = imc.map(map_func)

    

    # imc = imc.map(lambda img: img.rename('classification'))



    def iterate_func(img, prev):

        img = ee.Image(img).select('classification')
        year = ee.String(img.get('year'))
        band_name = ee.String(img.get('band_name'))
        img = ee.Image(prev).addBands(img.rename(band_name))
        return img

    first_image = ee.Image(imc.first())
  
    image = ee.Image(imc.iterate(iterate_func, first_image) )

    image = image.select(image.bandNames().remove('classification'))
  
    return image
  
def readParamsTable(tableName):
    """Read parameters table"""

    table = []

    with open(tableName) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            table.append({
                'grid_name': row['GRID_NAME'],
                'biome': row['BIOME'],
                'process': int(row['PROCESS']),
                'account': int(row['ACCOUNT'])
            })

    return table


def toImageCollection(image):
    def map_func(name):
        year = ee.String(name).slice(15) 
        img = image.select([name]) \
                    .set('band_name',name) \
                    .set('year',year) \
                    .set('system:time_start', year.cat(ee.String('-01-01'))) \
                    .rename('classification') 
        return img

    bandNamesList = image.bandNames()
    imc = bandNamesList.map(map_func)
  
    return ee.ImageCollection.fromImages(imc)

def remapCloud(imc):
    def iterate_func(img, prev):
        img_ = ee.Image(img).select('classification')
        prev_ = ee.Image(prev).select('classification')
        year = ee.String(img_.get('year'))
        band_name = ee.String(img.get('band_name'))

        img_f = img_.where(prev_.eq(24).And(img_.eq(27)), 24)
        img_f = ee.Image(prev).addBands(img_f.rename(band_name))
        return img_f
  
    first_image = ee.Image(imc.first())
  
    image_ft = ee.Image(imc.iterate(iterate_func, first_image) )
  
    return image_ft.select(image_ft.bandNames().remove('classification'))


def applyFilterCloud(image):
    imc = toImageCollection(image).sort('system:time_start')

    image = remapCloud(imc)

    imc = toImageCollection(image).sort('system:time_start', False)

    image = remapCloud(imc)

    return image.where(image.eq(27), 0)


def applyFilterFreq(image):
    imc = toImageCollection(image).sort('system:time_start')



    freq = image.eq(24).reduce(ee.Reducer.sum())
    freq_last_years = image.select(['classification_2017','classification_2018']).eq(24).reduce(ee.Reducer.sum())
    imc = imc.map(lambda img: img.where(freq_last_years.eq(0).And(freq.lt(3)), 0))

    
    image = ImcToImage(imc)
    
    freq = image.eq(24).reduce(ee.Reducer.sum())
    freq_last_3years = image.select(['classification_2016','classification_2017','classification_2018']).eq(24).reduce(ee.Reducer.sum())
    
    imc = toImageCollection(image)
    

    imc = imc.map(lambda img: img.where(freq_last_3years.eq(0).And(freq.lt(4)), 0))
   
    image = ImcToImage(imc)
    
    freq = image.eq(24).reduce(ee.Reducer.sum())
    freq_last_3years = image.select(['classification_2016','classification_2017','classification_2018']).eq(24).reduce(ee.Reducer.sum())
    freq_first_3years = image.select(['classification_1985','classification_1986','classification_1987']).eq(24).reduce(ee.Reducer.sum())

    imc = imc.map(lambda img: img.where(freq_last_3years.gt(1).And(freq_first_3years.gt(1)).And(freq.gt(20)), 24))


    return ImcToImage(imc)





    

