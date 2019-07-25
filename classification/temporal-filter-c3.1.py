# coding: utf-8
import ee
import csv

ee.Initialize()

#
# control task parameters
#
account = 1



rule_ft_csv = './regras-filtro-temporal-area-urbana.csv'
rule_pos_ft_csv = './regras-pos-filtro-temporal-area-urbana.csv'


cartas = ee.FeatureCollection("projects/mapbiomas-workspace/AUXILIAR/cartas")

# cartas = ee.FeatureCollection(cartas.filterMetadata('grid_name', 'equals', 'SC-25-V-A'))


#
# temporal filter parameters
#
params = {

    "asset": {
        "classificacao": "projects/mapbiomas-workspace/TRANSVERSAIS/INFRAURBANA3-DEV",
        "classificacaoft": "users/dyedenterras/TRANSVERSAIS/INFRAURBANA",
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
        'classification_2017'
    ]
}

#
# spatial filter parameters
#
filterParams = [
    {
        'classValue': 1,
        'maxSize': 5
    },
    {
        'classValue': 27,
        'maxSize': 5
    },
    {
        'classValue': 0,
        'maxSize': 5
    }
]


class TemporalFilter(object):

    options = {

        "rulesft": 'ft:15cCjWV5BeQjW1htgz1gzG7fSqa2MgTUUbSCqOwrs',

        "asset": {
        },

        "ft_rules": {},

        'bands': []

    }

    def __init__(self, params):

        self.params = params

        self.options.update(params)

        self.loadRules()

        self.loadRulesPosFT()

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

    
    def loadRulesPosFT(self):

        self.options['posft_rules'] = {
            'rpk3': filter(lambda rule:
                           rule['type'] == 'RP' and rule['kernel'] == 3,
                           self.params['posft_rules']
                           ),
            'rgk3': filter(lambda rule:
                           rule['type'] == 'RG' and rule['kernel'] == 3,
                           self.params['posft_rules']
                           ),
            'ruk3': filter(lambda rule:
                           rule['type'] == 'RU' and rule['kernel'] == 3,
                           self.params['posft_rules']
                           ),
            'rpk5': filter(lambda rule:
                           rule['type'] == 'RP' and rule['kernel'] == 5,
                           self.params['posft_rules']
                           ),
            'rgk5': filter(lambda rule:
                           rule['type'] == 'RG' and rule['kernel'] == 5,
                           self.params['posft_rules']
                           ),
            'ruk5': filter(lambda rule:
                           rule['type'] == 'RU' and rule['kernel'] == 5,
                           self.params['posft_rules']
                           )
        }

    def temporalFilter33_fillMissing(self, image):
        image_original = image
        image = image_original.where(image_original.neq(1), 0)
        freq = image.reduce(ee.Reducer.sum())
        
        last3years = image.select(["classification_2015", "classification_2016", "classification_2017"])
        freq_last3years = last3years.reduce(ee.Reducer.sum())


        first3years = image.select(["classification_1985", "classification_1986", "classification_1987"])
        freq_first3years = first3years.reduce(ee.Reducer.sum())

        mask = freq.multiply(0)
        mask = mask.where(freq.gte(26), 1)
        mask = mask.where(freq_last3years.lt(3).And(freq_first3years.lt(3)), 0)

        image = image.where(mask.eq(1), 1)

        return image

    
    def temporalFilter33_removeNoise(self, image):
        freq = image.reduce(ee.Reducer.sum())

        last3years = image.select(["classification_2015", "classification_2016", "classification_2017"])
        freq_last3years = last3years.reduce(ee.Reducer.sum())

        mask = freq.multiply(0)
        mask = mask.where(freq.lte(3), 1)
        mask = mask.where(freq_last3years.gt(1), 0)

        image = image.where(mask.eq(1), 0)

        return image



    def getCollection(self):

        # image = ee.Image( self.options['asset']['classificacao'] + "/SC-25-V-A")
        image = ee.ImageCollection(self.options['asset']['classificacao']).mosaic()

        image = self.temporalFilter33_removeNoise(image)

        return image

    def list2multband(self, imageList):

        image = imageList[0]

        n = len(imageList)

        for band in imageList[1:n]:
            image = image.addBands(band)

        return image

    def noData2NotObserved(self, image):
        """
        Reclassify the no data value to not observed class value
        """
        # image = ee.Image(image)
        # image = image.where(image.eq(0), 27).copyProperties(image)

        image = ee.Image(image)

        image = image.unmask(27).copyProperties(image) 

        return ee.Image(image)

    def fillHoles(self, image):

        image = ee.Image(image)

        image = ee.Image(27).where(image.gte(0), image)\
            .clip(cartas)\
            .rename(image.bandNames())\
            .copyProperties(image)
        
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


    def applyRules(self):

        image = self.getCollection()

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

        for rule in self.options['ft_rules']['ruk5']:
            imageList[n-1] = self.applyRuleKernel5(
                imageList,
                rule,
                [n-5, n-4, n-3, n-2, n-1],
                n-1
            )

        # rules kernel 3
        for rule in self.options['ft_rules']['rpk3']:
            imageList[0] = self.applyRuleKernel3(
                imageList,
                rule,
                [0, 1, 2],
                0
            )

        for i in range(1, n-2):
            for rule in self.options['ft_rules']['rgk3']:
                imageList[i] = self.applyRuleKernel3(
                    imageList,
                    rule,
                    [i-1, i, i+1],
                    i
                )

        for rule in self.options['ft_rules']['ruk3']:
            imageList[n-1] = self.applyRuleKernel3(
                imageList,
                rule,
                [n-3, n-2, n-1],
                n-1
            )

        # filtered = self.list2multband(imageList)

        return imageList

#
#  Classe de pos-classificação para reduzir ruídos na imagem classificada
#
#  @param {ee.Image} image [eeObjeto imagem de classificação]
#
#  @example
#  var image = ee.Image("aqui vem a sua imagem");
#  var filterParams = [
#      {classValue: 1, maxSize: 3},
#      {classValue: 2, maxSize: 5}, // o tamanho maximo que o mapbiomas está usado é 5
#      {classValue: 3, maxSize: 5}, // este valor foi definido em reunião
#      {classValue: 4, maxSize: 3},
#      ];
#  var pc = new PostClassification(image);
#  var filtered = pc.spatialFilter(filterParams);
#


class PostClassification(object):

    def __init__(self, image):

        self.image = ee.Image(image)

    def _majorityFilter(self, params):

        # Generate a mask from the class value
        classMask = self.image.eq(params['classValue'])

        # Labeling the group of pixels until 100 pixels connected
        labeled = classMask.mask(classMask).connectedPixelCount(100, True)

        # Select some groups of connected pixels
        region = labeled.lt(params['maxSize'])

        # Squared kernel with size shift 1
        # [[p(x-1,y+1), p(x,y+1), p(x+1,y+1)]
        # [ p(x-1,  y), p( x,y ), p(x+1,  y)]
        # [ p(x-1,y-1), p(x,y-1), p(x+1,y-1)]
        kernel = ee.Kernel.square(1)

        # Find neighborhood
        neighs = self.image.neighborhoodToBands(kernel).mask(region)

        # Reduce to majority pixel in neighborhood
        majority = neighs.reduce(ee.Reducer.mode())

        # Replace original values for new values
        filtered = self.image.where(region, majority)

        return filtered.byte()

    #
    # Método para reclassificar grupos de pixels de mesma classe agrupados
    # @param  {list<dictionary>} filterParams [{classValue: 1, maxSize: 3},{classValue: 2, maxSize: 5}]
    # @return {ee.Image}  Imagem classificada filtrada
    #
    def spatialFilter(self, filterParams):

        for params in filterParams:
            self.image = self._majorityFilter(params)

        return self.image


def cloudSeriesFilter(image, bandNames):

    # bandNames1 = ee.List(list(reversed(bandNames)))

    bandNames1 = bandNames

    # Corrige os primeiros anos. Aplica o filtro de tras pra frente
    filtered = ee.List(bandNames1).iterate(
        lambda bandName, previousImage:
            image.select(ee.String(bandName)).where(
                image.select(ee.String(bandName)).eq(27),
                ee.Image(previousImage).select([0])
            ).addBands(ee.Image(previousImage)),
        ee.Image(image.select(["classification_2016"]))
    )

    filtered = ee.Image(filtered)

    # Corrige os ultimos anos. Aplica o filtro da frente pra tras
    filtered2 = ee.List(bandNames).iterate(
        lambda bandName, previousImage:
            ee.Image(previousImage).addBands(
                filtered.select(ee.String(bandName)).where(
                    filtered.select(ee.String(bandName)).eq(27),
                    ee.Image(previousImage).select(ee.Image(previousImage).bandNames().length().subtract(1)))),
        ee.Image(filtered.select(["classification_2000"]))
    )

    filtered2 = ee.Image(filtered2)

    return filtered2
#----------------------------------------------------------------------
# Script to run the temporal filter and export images
#----------------------------------------------------------------------


# import ee.mapclient

ee.Initialize()


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


def applySpatialFilter(nextImage, image):

    pc = PostClassification(nextImage)

    spatialFiltered = pc.spatialFilter(filterParams)

    return ee.Image(image).addBands(ee.Image(spatialFiltered))

def start():

    params['ft_rules'] = []
    

    with open(rule_ft_csv, 'rb') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        for row in data:
            params['ft_rules'].append(row)


    params['posft_rules'] = []

    with open(rule_pos_ft_csv, 'rb') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        for row in data:
            params['posft_rules'].append(row)

    tf = TemporalFilter(params)


    collectiontf = tf.applyRules()
    
    collection = tf.getCollection()

    image = ee.Image(collectiontf[0])

    pc = PostClassification(image)

    spatialFiltered = pc.spatialFilter(filterParams)


    filtered = ee.List(collectiontf[1:]).iterate(
        applySpatialFilter, spatialFiltered)

    filtered = ee.Image(filtered)

    filtered = cloudSeriesFilter(filtered, params['bands'])

    VIIRSLight = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')

    VIIRSLight = VIIRSLight.filterDate('2017-01-01', '2018-04-30')

    VIIRSLight = VIIRSLight.median().select('avg_rad').gt(3).toByte()

    mask_light = VIIRSLight.clip(cartas)
    
    filtered = tf.temporalFilter33_fillMissing(filtered)

    filtered = tf.applyRulesNotCumulative(filtered)

    filtered = tf.applyRulesNotCumulative(filtered)

    filtered = tf.temporalFilter33_fillMissing(filtered)

    filtered = filtered.where(mask_light.eq(0).And(filtered.eq(1)), 0)

    imageName = "infraurbana_vfinal"

    task = ee.batch.Export.image.toAsset(
        filtered.toByte(),
        description=imageName,
        assetId=params['asset']['classificacaoft'] + '/' + imageName,
        region=cartas.union().geometry().getInfo()['coordinates'],
        scale=30,
        pyramidingPolicy='{".default":"mode"}',
        maxPixels=1e13
    )

    task.start()

    print(task.status())




start()
