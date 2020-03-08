from django.shortcuts import render
from django.template.loader import render_to_string
from zap_apps.zap_catalogue.product_serializer import AndroidProductsToApproveSerializer, NumberOfProductSrlzr
from zap_apps.account.zapauth import ZapView, ZapAuthView
import re
from zap_apps.zap_catalogue.product_serializer import ProductImageSerializer
from zap_apps.zap_catalogue.models import ApprovedProduct, Size, NumberOfProducts, Hashtag
from django.conf import settings
from zap_apps.zap_notification.views import ZapSms, ZapEmail
# Create your views here.
from zap_apps.zap_upload.upload_serializer import (GetApprovedProductStep1, GetApprovedProductStep2, 
    GetApprovedProductStep3, UpdateApprovedProductSerializerAndroid,
    UploadPage1An, UploadPage2An, UploadPage3An, UploadPage4An, ProPicSrlzr,
    GetPTAStep1, GetPTAStep2,GetPTAStep2PUT, GetPTAStep3, UpdatePTASerializerAndroid)
from zap_apps.zap_notification.tasks import zaplogging
from django.db import IntegrityError



class ProPic(ZapAuthView):
    def post(self, request, format=None):
        data = request.data.copy()
        srlzr = ProPicSrlzr(request.user.profile, data=data, partial=True)
        if not srlzr.is_valid():
            return self.send_response(0, srlzr.errors)
        srlzr.save()
        return self.send_response(1, "Profile picture updated successfully")


class EditAlbum(ZapAuthView):

    def get(self, request, product_id, step, format=None):
        #if request.GET.get('action') == 'p_t_a':
        try:
            product = ApprovedProduct.objects.get(id=product_id, user=request.user)
        except ApprovedProduct.DoesNotExist:
            return self.send_response(0, 'No such product')
        if int(step) == 1:
            serlzr = GetPTAStep1(product)
            return self.send_response(1, serlzr.data)
        elif int(step) == 2:
            serlzr = GetPTAStep2(product)
            return self.send_response(1, serlzr.data)
        elif int(step) == 3:
            serlzr = GetPTAStep3(product)
            return self.send_response(1, serlzr.data)


    def put(self, request, product_id, step, format=None):
        data = request.data.copy()
        print data
        if request.GET.get('action') == 'p_t_a':
            try:
                product = ApprovedProduct.objects.get(id=product_id, user=request.user)
            except ProductsToApprove.DoesNotExist:
                return self.send_response(0, 'No such product.')
            if int(step) == 1:
                image_list = data['old_images']
                new_images = data['images']
                img_ids = []
                for i in new_images:
                    img_serializer = ProductImageSerializer(data={'image': i})
                    if img_serializer.is_valid():
                        while True:
                            try:
                                img_serializer.save()
                                break
                            except IntegrityError:
                                pass
                        img_ids.append(img_serializer.data['id'])
                    else:
                        return self.send_response(0, img_serializer)
                data['images'] = list(image_list + img_ids)
                if len(data['images']) > 6:
                    return self.send_response(0, "Maximum number of upload images limit exeeded")
                if data.get('sub_category'):
                    data['product_category'] = data['sub_category']
                data['completed'] = True if data['sale'] == '1' else False
                if 'size' in data:
                    new_size_ids = []
                    msg = "edit-put-98"+str(data)
                    zaplogging.delay(msg) if settings.CELERY_USE else zaplogging(msg)
                    if data['size'][0] == '' or data['size'][0]['id'] == 'freesize' or (data.get('size_type') and data['size_type'].lower() == 'freesize') or Size.objects.filter(id=data['size'][0]['id'],category_type="FS").exists():
                        size = Size.objects.get(category_type="FS")
                        try:
                            quantity = data['size'][0]['qty']
                        except TypeError:
                            quantity = 1
                        n_o_p = NumberOfProducts(size=size,quantity=quantity,product_id=product.id)
                        n_o_p.save()
                        product.size_type='FREESIZE'
                        product.save()
                        new_size_ids.append(n_o_p.id)
                    else:
                        for s in data['size']:
                            if NumberOfProducts.objects.filter(size_id=s['id'],product_id=product.id):
                                pass
                            else:
                                n_o_p = NumberOfProducts(size_id=s['id'],quantity=s['qty'],product_id=product.id)
                                n_o_p.save()
                                new_size_ids.append(n_o_p.id)
                    data['size'] = new_size_ids
                    print data['size'],'########'
                serlzr = UpdatePTASerializerAndroid(product, data=data, partial=True)
                if serlzr.is_valid():
                    if 'size' in data:
                        old_sizes = NumberOfProducts.objects.filter(product_id=product.id).exclude(id__in=new_size_ids).delete()
                    serlzr.save()
                else:
                    NumberOfProducts.objects.filter(id__in=new_size_ids).delete()
                    return self.send_response(0, serlzr.errors)
                return self.send_response(1, 'Success')
            elif int(step) == 2:
                serlzr = GetPTAStep2PUT(product, data=data, partial=True)
                #serlzr = GetPTAStep2(product, data=data, partial=True)
                if serlzr.is_valid():
                    serlzr.save()
                    return self.send_response(1, 'Success')
                else:
                    return self.send_response(0, serlzr.errors)
            elif int(step) == 3:
                data['completed'] = True
                serlzr = GetPTAStep3(product, data=data)
                if serlzr.is_valid():
                    serlzr.save()
                    return self.send_response(1, 'Success')
                else:
                    return self.send_response(0, serlzr.errors)
            return self.send_response(0, 'invalid step')
        else:
            try:
                product = ApprovedProduct.objects.get(id=product_id, user=request.user)
            except ApprovedProduct.DoesNotExist:
                return self.send_response(0, 'No such product.')
            if int(step) == 1:
                image_list = data['old_images']
                new_images = data['images']
                img_ids = []
                for i in new_images:
                    img_serializer = ProductImageSerializer(data={'image': i})
                    if img_serializer.is_valid():
                        while True:
                            try:
                                img_serializer.save()
                                break
                            except IntegrityError:
                                pass
                        img_ids.append(img_serializer.data['id'])
                    else:
                        return self.send_response(0, img_serializer)
                data['images'] = list(image_list + img_ids)
                if data.get('sub_category'):
                    data['product_category'] = data['sub_category']
                data['completed'] = True if data['sale'] == '1' else False
                if 'size' in data:
                    new_size_ids = []
                    msg = "edit-put-161"+str(data)
                    zaplogging.delay(msg) if settings.CELERY_USE else zaplogging(msg)
                    if data['size'][0] == '' or data['size'][0]['id'] == 'freesize' or (data.get('size_type') and data['size_type'].lower() == 'freesize') or Size.objects.filter(id=data['size'][0]['id'],category_type="FS").exists():
                        size = Size.objects.get(category_type="FS")
                        try: 
                            quantity = data['size'][0]['qty']
                        except TypeError:
                            quantity = 1
                        n_o_p = NumberOfProducts(size=size,quantity=quantity,product_id=product.id)
                        n_o_p.save()
                        product.size_type='FREESIZE'
                        product.save()
                        new_size_ids.append(n_o_p.id)
                    else:
                        for s in data['size']:
                            n_o_p = NumberOfProducts(size_id=s['id'],quantity=s['qty'],product_id=product.id)
                            n_o_p.save()
                            new_size_ids.append(n_o_p.id)
                    data['size'] = new_size_ids
                serlzr = UpdateApprovedProductSerializerAndroid(product, data=data, partial=True)
                if serlzr.is_valid():
                    if 'size' in data:
                        old_sizes = NumberOfProducts.objects.filter(product_id=product.id).exclude(id__in=new_size_ids).delete()
                    serlzr.save()
                else:
                    return self.send_response(0, serlzr.errors)
                return self.send_response(1, 'Success')

            elif int(step) == 2:
                serlzr = GetApprovedProductStep2(product, data=data, partial=True)
                if serlzr.is_valid():
                    serlzr.save()
                    return self.send_response(1, 'Success')
                else:
                    return self.send_response(0, serlzr.errors)
            elif int(step) == 3:
                serlzr = GetApprovedProductStep3(product, data=data, partial=True)
                if serlzr.is_valid():
                    serlzr.save()
                    return self.send_response(1, 'Success')
                else:
                    return self.send_response(0, serlzr.errors)
            return self.send_response(0, 'invalid step')

class AlbumCRUD(ZapAuthView):
    def post(self, request, product_id, format=None):
        data = request.data.copy()
        print data
        data['user'] = request.user.id
        if product_id:
            serlzr = UploadPage2An(data={'product_id':product_id})
            if not serlzr.is_valid():
                return self.send_response(0, serlzr.errors)
            required_keys = ['images','original_price','pickup_address']
            if not  any(i in data for i in required_keys):
                return self.send_response(0, "No required keys ['images/original_price/pickup_address']")
            try:
                product = ApprovedProduct.objects.get(
                    id=product_id, user=request.user)
            except ApprovedProduct.DoesNotExist:
                return self.send_response(0, "No such product")

            if 'images' in data:
                if not (data['images'] and isinstance(data['images'],list)):
                    return self.send_response(0, "invalid format for key 'image'")
                img_ids = []
                for i in data['images']:
                    img_serializer = ProductImageSerializer(data={'image': i})
                    if not img_serializer.is_valid():
                        return self.send_response(0, img_serializer.errors)
                    while True:
                        try:
                            img_serializer.save()
                            break
                        except IntegrityError:
                            pass
                    img_ids.append(img_serializer.data['id'])
                while True:
                    try:
                        product.images.add(*img_ids)
                        break
                    except IntegrityError:
                        pass
                if product.sale == '1':
                    product.completed = True
                    product.save()
                    zapemail = ZapEmail()
                    internal_html = settings.UPLOAD_ALBUM_INTERNAL_HTML
                    html = settings.UPLOAD_ALBUM_HTML
                    
                    internal_email_vars = {
                        'user': request.user.get_full_name(),
                        'type': product.get_sale_display(),
                        'album_name': product.title
                    }
                    
                    internal_html_body = render_to_string(
                    internal_html['html'], internal_email_vars)

                    zapemail.send_email_alternative(internal_html[
                                        'subject'], settings.FROM_EMAIL, "zapyle@googlegroups.com", internal_html_body)
                    
                    
                    # zapemail.send_email(internal_html['html'], internal_html[
                    #                     'subject'], email_vars, settings.FROM_EMAIL, "zapyle@googlegroups.com")
                    # import pdb; #######pdb.set_trace()
                    email_vars = {
                        'user': request.user.get_full_name()
                    }

                    html_body = render_to_string(
                    html['html'], email_vars)

                    zapemail.send_email_alternative(html[
                                        'subject'], settings.FROM_EMAIL, request.user.email, html_body)

                    # zapemail.send_email(html['html'], html[
                    #                     'subject'], email_vars, settings.FROM_EMAIL, request.user.email)
                    zapsms = ZapSms()
                    zapsms.send_sms(request.user.phone_number, settings.UPLOAD_LIST_NEW_MSG)
                return self.send_response(1, "Image uploaded succefully.")
            elif 'original_price' in data:
                if request.user.user_type.name == 'store_front':
                    data['age'] = '0'
                    data['condition'] = '0'
                serlzr = UploadPage3An(data=data)
                if not serlzr.is_valid():
                    return self.send_response(0, serlzr.errors)
                serlzr = AndroidProductsToApproveSerializer(product, data=data, partial=True)
                if not serlzr.is_valid():
                    return self.send_response(0, serlzr.errors)
                serlzr.save()
                return self.send_response(1, "price added Succefully.")
            elif 'pickup_address' in data:
                serlzr = UploadPage4An(data=data)
                if not serlzr.is_valid():
                    return self.send_response(0, serlzr.errors)
                serlzr = AndroidProductsToApproveSerializer(product, data={'pickup_address':data['pickup_address'],'completed':True}, partial=True)
                if not serlzr.is_valid():
                    return self.send_response(0, serlzr.errors)
                p_t_a = serlzr.save()
                zapemail = ZapEmail()
                internal_html = settings.UPLOAD_ALBUM_INTERNAL_HTML
                html = settings.UPLOAD_ALBUM_HTML
                
                internal_email_vars = {
                    'user': request.user.get_full_name(),
                    'type': p_t_a.get_sale_display(),
                    'album_name': p_t_a.title
                }

                internal_html_body = render_to_string(
                internal_html['html'], internal_email_vars)

                zapemail.send_email_alternative(internal_html[
                                    'subject'], settings.FROM_EMAIL, "zapyle@googlegroups.com", internal_html_body)

                # zapemail.send_email(internal_html['html'], internal_html[
                #                     'subject'], email_vars, settings.FROM_EMAIL, "zapyle@googlegroups.com")
                email_vars = {
                    'user': request.user.get_full_name()
                }

                html_body = render_to_string(
                html['html'], email_vars)

                zapemail.send_email_alternative(html[
                                    'subject'], settings.FROM_EMAIL, request.user.email, html_body)
                
                # zapemail.send_email(html['html'], html[
                #                     'subject'], email_vars, settings.FROM_EMAIL, request.user.email)
                zapsms = ZapSms()
                zapsms.send_sms(request.user.phone_number, settings.UPLOAD_LIST_NEW_MSG)
                return self.send_response(1, "Address added Succefully.")

        serlzr = UploadPage1An(data=data)
        if not serlzr.is_valid():
            return self.send_response(0, serlzr.errors)
        data['product_category'] = data['sub_category']
        if not ('size' in data and data['size'] and isinstance(data['size'],list) \
        and all(isinstance(i, dict) for i in data['size']) and \
        all((j in ['id','qty'] for j in i.keys()) for i in data['size'])):
            return self.send_response(0, "size required eg: size = [{'id':'freesize','qty':1}]")
        serlzr = AndroidProductsToApproveSerializer(data=data)
        if serlzr.is_valid():
            words = re.findall('#\S', data['description'])
            if words:
                for i in words:
                    Hashtag.objects.get_or_create(tag=i)
            p_t_a = serlzr.save()
            # data_to_numofproducts = {
            # 	'size': Size.objects.get(category_type="FS").id if data.get('global_size')=="Free Size" else data.get('global_size'),
            # 	'product_to_approve': p_t_a.id}
            msg = "albmcrud-post-345"+str(data)
            zaplogging.delay(msg) if settings.CELERY_USE else zaplogging(msg)
            print data,'---------------------'
            if data['size'][0] == '' or data['size'][0]['id'] == 'freesize' or (data.get('size_type') and data['size_type'].lower() == 'freesize') or Size.objects.filter(id=data['size'][0]['id'],category_type="FS").exists():
                try: 
                    quantity = data['size'][0]['qty']
                except TypeError:
                    quantity = 1
                data_to_numofproducts = {
                    'size': Size.objects.get(category_type="FS").id,
                    'product': p_t_a.id,
                    'quantity': quantity}
                p_t_a_srlzr = NumberOfProductSrlzr(data=data_to_numofproducts)
                if p_t_a_srlzr.is_valid():
                    p_t_a_srlzr.save()
                    p_t_a.size_type='FREESIZE'
                    p_t_a.save()
                else:
                    print p_t_a_srlzr.errors, ' errors11'
            else:
                for size_selected in data['size']:
                    data_to_numofproducts = {
                        'size': size_selected['id'],
                        'product': p_t_a.id,
                        'quantity': size_selected['qty']}
                    p_t_a_srlzr = NumberOfProductSrlzr(
                        data=data_to_numofproducts)
                    print data_to_numofproducts,'data_to_numofproducts'
                    if p_t_a_srlzr.is_valid():
                        p_t_a_srlzr.save()
                    else:
                        print p_t_a_srlzr.errors, ' errors22'

            # p_t_a_srlzr = NumberOfProductSrlzr(data=data_to_numofproducts)
            # if not p_t_a_srlzr.is_valid():
            # 	return self.send_response(0, srlzr.errors)
            # p_t_a_srlzr.save()

            return self.send_response(1, {"product_id": p_t_a.id})
        return self.send_response(0, serlzr.errors)



class ImageUpload(ZapAuthView):

    def post(self, request, product_id, format=None):
        data = request.data.copy()
        data['user'] = request.user.id
        if product_id:
            action = request.GET.get('action','')
            if action == 'p_t_a':
                required_keys = ['image']
                if not  any(i in data for i in required_keys):
                    return self.send_response(0, "No required keys ['image/add']")
                try:
                    product = ApprovedProduct.objects.get(
                        id=product_id)#, user=request.user)
                except ProductsToApprove.DoesNotExist:
                    return self.send_response(0, "No such product")
                print product.images.all()
                if product.images.count() >= 6:
                    return self.send_response(0, "Maximum number of upload images limit exeeded")
                img_serializer = ProductImageSerializer(data={'image':data['image']})
                if not img_serializer.is_valid():
                    return self.send_response(0, img_serializer.errors)
                while True:
                    try:
                        img_serializer.save()
                        break
                    except IntegrityError:
                        pass
                while True:
                    try:
                        product.images.add(img_serializer.data['id'])
                        break
                    except IntegrityError:
                        pass
                return self.send_response(1, "Image uploaded Succefully.")
            else:
                required_keys = ['image']
                if not  any(i in data for i in required_keys):
                    return self.send_response(0, "No required keys ['image/add']")
                try:
                    product = ApprovedProduct.objects.get(
                        id=product_id)#, user=request.user)
                except ApprovedProduct.DoesNotExist:
                    return self.send_response(0, "No such product")
                print product.images.all()
                if product.images.count() >= 6:
                    return self.send_response(0, "Maximum number of upload images limit exeeded")
                img_serializer = ProductImageSerializer(data={'image':data['image']})
                if not img_serializer.is_valid():
                    return self.send_response(0, img_serializer.errors)
                while True:
                    try:
                        img_serializer.save()
                        break
                    except IntegrityError:
                        pass
                while True:
                    try:
                        product.images.add(img_serializer.data['id'])
                        break
                    except IntegrityError:
                        pass
                return self.send_response(1, "Image uploaded Succefully.")