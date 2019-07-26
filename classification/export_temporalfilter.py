import ee
import temporalfilter_lib as tf_lib
import csv

ee.Initialize()

def start():
    tf_lib.params['ft_rules'] = []



    with open(tf_lib.rule_ft_csv, 'rb') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        for row in data:
            tf_lib.params['ft_rules'].append(row)

    tf = tf_lib.TemporalFilter(tf_lib.params)

    image = tf.getClassificacao()

    

    image_tf = tf_lib.applyFilterCloud(image)
    

    image_tf = tf_lib.applyFilterFreq(image_tf)
     
    
    collectiontf = tf.applyRules(image_tf)

    imagetf = tf_lib.ImcToImage(ee.ImageCollection.fromImages(collectiontf))

    # print(imagetf.getInfo())

    imageName = "infraurbana_v1"

    task = ee.batch.Export.image.toAsset(
        imagetf.toByte(),
        description=imageName,
        assetId=tf_lib.params['asset']['classificacaoft'] + '/' + imageName,
        region=tf_lib.cartas.union().geometry().getInfo()['coordinates'],
        scale=30,
        pyramidingPolicy='{".default":"mode"}',
        maxPixels=1e13
    )

    task.start()

    print(task.status())

 

start()