import ee
import temporalfilter_lib as tf_lib
import csv
import pprint

ee.Initialize()

def start():
    tf_lib.params['ft_rules'] = []



    with open(tf_lib.rule_ft_csv, 'rb') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        for row in data:
            row['kernel'] = int(row['kernel'])
            tf_lib.params['ft_rules'].append(row)

    tf = tf_lib.TemporalFilter(tf_lib.params)

    image = tf.getClassificacao()

    image_tf = tf_lib.applyFilterCloud(image)
    

    image_tf = tf_lib.applyFilterFreq(image_tf)
    

    image_tf = tf.applyRules(image_tf)


    # imageName = "infraurbana_v3"

    # task = ee.batch.Export.image.toAsset(
    #     image_tf.toByte(),
    #     description=imageName,
    #     assetId=tf_lib.params['asset']['classificacaoft'] + '/' + imageName,
    #     region=tf_lib.cartas.union().geometry().getInfo()['coordinates'],
    #     scale=30,
    #     pyramidingPolicy='{".default":"mode"}',
    #     maxPixels=1e13
    # )

    # task.start()

    # print(task.status())

 

start()