#elasticsearch document by mohamed shafi ck

data = {
	'mappings': {
		'products': {
			'properties': {
				'i_brand': {'index': 'not_analyzed','type': 'string'},
    			'i_category': {'index': 'not_analyzed', 'type': 'string'},
			    'i_color': {'index': 'not_analyzed', 'type': 'string'},
			    'i_occasion': {'index': 'not_analyzed', 'type': 'string'},
			    'i_product_category': {'index': 'not_analyzed', 'type': 'string'},
			    'i_style': {'index': 'not_analyzed', 'type': 'string'}
			}
		}
	},
 	'settings': {'number_of_replicas': 1, 'number_of_shards': 4}
}

response = requests.put('http://127.0.0.1:9200/production/',data=json.dumps(data))

print response.text

#bulk upload products

data = ''
for p in ApprovedProduct.ap_objects.all():
    data += '{"index": {"_id": "%s"}}\n' % p.id
    data += json.dumps(ElasticProductsSerializer(p).data) + '\n'

response = requests.put('http://127.0.0.1:9200/production/products/_bulk', data=data)