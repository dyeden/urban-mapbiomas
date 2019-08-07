import ee
import temporalfilter_lib as tf_lib
import csv
import pprint

ee.Initialize()

def start():
    tf_lib.params['ft_rules'] = []



    with open(tf_lib.rule_ft_csv, 'r') as csvfile:
        data = csv.DictReader(csvfile, delimiter=',', quotechar='|')
        for row in data:
            row['kernel'] = int(row['kernel'])
            row['result'] = int(row['result'])
            tf_lib.params['ft_rules'].append(row)

tf = tf_lib.TemporalFilter(tf_lib.params)

image = tf.getClassificacao()

image_tf = tf_lib.applyFilterCloud(image)