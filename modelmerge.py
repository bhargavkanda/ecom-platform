import sys,os,csv
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "zapyle_new.settings.local"
django.setup()

from zap_apps.zap_catalogue.models import ApprovedProduct

#add field status to model ApprovedProduct
ApprovedProduct.objects.update(status=1)
from zap_apps.zap_upload.models import *
from zap_apps.zap_admin.admin_serializer import *
for prdt in ProductsToApprove.objects.all():
	print prdt.id,'iddd'
	serlzr = GetProductsToApproveSerializer(prdt)
	data =serlzr.data
	data['status'] = '0'
	approvedSrlzr = ApprovedProductSerializer(data=data)
	if approvedSrlzr.is_valid():
		p = approvedSrlzr.save()
	else:
		print 'error ',prdt.id,' -- ',approvedSrlzr.errors
	if prdt.user.user_type.name == 'zap_exclusive' and prdt.zapexclusiveuserdata_set.all():
		zap_exc_obj = prdt.zapexclusiveuserdata_set.all()[0]
		zap_exc_obj.products_to_approve.remove(prdt)
		zap_exc_obj.products.add(p.id)
	n_o_p = NumberOfProducts.objects.filter(
		product_to_approve_id=prdt.id).update(product_to_approve=None, product=p)


for prdt in DisapprovedProduct.objects.all():
	print prdt.id
	serlzr = GetDisapprovedProductsSerializer(prdt)
	data =serlzr.data
	data['status'] = '2'
	approvedSrlzr = ApprovedProductSerializer(data=data)
	if approvedSrlzr.is_valid():
		p = approvedSrlzr.save()
		n_o_p = NumberOfProducts.objects.filter(
			disapproved_product_id=prdt.id).update(disapproved_product=None, product=p) 
	else:
		print 'error ',prdt.id,' -- ',approvedSrlzr.errors



