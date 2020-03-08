from django.shortcuts import render
from django.http import HttpResponseRedirect
from zap_apps.blog.models import BloggersMeetUpRegistration
from rest_framework.decorators import api_view
from django.contrib.admin.views.decorators import staff_member_required
from zap_apps.account.zapauth import admin_only
from zap_apps.account.zapauth import ZapView
from rest_framework.response import Response
from time import time
import os
from django.conf import settings
from zap_apps.blog.blog_serializers import *
from zap_apps.blog.models import *
from zap_apps.blog.models import BlogLove as BL
from rest_framework.pagination import PageNumberPagination
from .forms import NameForm
from zap_apps.blog.tasks import saveImage, saveThumbs
import ast
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from zap_apps.zap_catalogue.models import ApprovedProduct


@api_view(['GET', 'POST', ])
# @staff_member_required
def editor(request, type, blog_id=None):
    if type == 'blog':
        return render(request, 'blog/blog-editor1.html')
    elif type == 'look':
        return render(request, 'blog/look-editor.html')


@api_view(['GET', 'POST', ])
def home(request):
    return render(request, 'blog/blog-list.html')


@api_view(['GET', 'POST', ])
def post(request, blog_id, blog_slug):
    try:
        blog = BlogPost.objects.get(id=blog_id)
        data = {'title': blog.title, 'category': blog.category.name, 'cover': blog.cover_pic, 'id': blog.id, 'slug': blog.slug}
        return render(request, 'blog/blog-post.html', data)
    except Exception:
        response = render(request, 'account/error_pages/404.html', {})
        response.status_code = 404
        return response



def BloggersMeetUp(request):
    if request.method == 'POST':
        data = request.POST
        form = NameForm(data)
        if form.is_valid():
            if BloggersMeetUpRegistration.objects.filter(email=data['email']):
                form.errors['email']=['This email is already registered']
                return render(request, 'blog/blog_meetup.html', {'name':data['name'],'phone':data['phone'],'email':data['email'],'city':data['city'],'form': form.errors})              
            BloggersMeetUpRegistration.objects.create(name=data['name'],email=data['email'],city=data['city'],phone=data['phone'])
            return render(request, 'blog/blog_meetup.html',{'success':True})        
        else:
            return render(request, 'blog/blog_meetup.html', {'name':data['name'],'phone':data['phone'],'email':data['email'],'city':data['city'],'form': form.errors})
    return render(request, 'blog/blog_meetup.html')


# def saveImage(b64_list):
#     if not os.path.exists(settings.MEDIA_ROOT + '/blog'):
#         os.makedirs(settings.MEDIA_ROOT + '/blog')
#     for b64 in b64_list:
#         header, data = b64['base64'].split(';base64,')
#         base64_string = data
#         filename = "blog_image%s.png" % str(time()).replace('.', '_')
#         fh = open(os.path.join(settings.MEDIA_ROOT + '/blog', filename), "wb")
#         fh.write(base64_string.decode('base64'))
#         fh.close()
#         print '/zapmedia/blog/' + filename
#         b64['base64'] = '/zapmedia/blog/' + filename

    
class Image(ZapView):

    def post(self, request, format=None):
        blog_media_path = settings.MEDIA_ROOT + '/blog'
        if not os.path.exists(blog_media_path):
            os.makedirs(blog_media_path)

        data = request.data.copy()
        blog_id = request.data.get('blog_id')
        blog_id_path = ''.join([blog_media_path, '/', str(blog_id)])
        if not os.path.exists(blog_id_path):
            os.makedirs(blog_id_path)

        if 'b64_list' in request.data:
            b64_list = request.data.get('b64_list')
            id = request.data.get('id')
            for b64 in b64_list:
                header, data = b64.split(';base64,')
                base64_string = data
                format = header.split('/')[1]
                filename = "blog_image%s.%s" % (str(time()).replace('.','_'), format)
                fh = open(os.path.join(blog_id_path, filename), "wb")
                fh.write(base64_string.decode('base64'))
                fh.close()
                file_path = ''.join(['/zapmedia/blog/', str(blog_id), '/', filename])
                print file_path
                if format != 'gif':
                    if settings.CELERY_USE:
                        saveThumbs.delay(blog_id_path + '/', filename)
                    else:
                        saveThumbs(blog_id_path + '/', filename)
            # b64['base64'] = file_path

            return Response({'status': 'success', 'url': file_path, 'id': id})
        elif 'files' in request.data:
            file = request.data.get('files')
            filename = file.name
            format = filename.split('.')[1]
            fout = open(os.path.join(blog_id_path, filename), 'wb+')
            file_content = ContentFile(file.read())
            try:
                # Iterate through the chunks.
                for chunk in file_content.chunks():
                    fout.write(chunk)
                fout.close()
                file_path = ''.join(['/zapmedia/blog/', str(blog_id), '/', filename])
                if format != 'gif':
                    if settings.CELERY_USE:
                        saveThumbs.delay(blog_id_path + '/', filename)
                    else:
                        saveThumbs(blog_id_path + '/', filename)
                return Response({'status': 'success', 'url': file_path})
            except Exception as e:
                return Response({'status': 'error', 'error': e.message})


class FormImage(ZapView):

    def post(self, request, format=None):
        blog_media_path = settings.MEDIA_ROOT + '/blog'
        if not os.path.exists(blog_media_path):
            os.makedirs(blog_media_path)



class AdminRequired(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(AdminRequired, cls).as_view(**initkwargs)
        return admin_only(view)


class BlogCRUD(ZapView):

    def get(self, request, post_id=None, format=None):
        if post_id:
            try:
                post = BlogPost.objects.get(id=post_id)
                if request.user.is_authenticated():
                    srlzr = SingleBlogPostSrlzr(post, context={'user': request.user})
                else:
                    srlzr = SingleBlogPostSrlzr(post, context={})
                return self.send_response(1, srlzr.data)
            except BlogPost.DoesNotExist:
                return self.send_response(0, {"error": "Blog DoesNotExist"})
        
        posts = BlogPost.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = BlogPostSrlzr(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, post_id=None, format=None):
        data = request.data.copy()
        product_ids = []
        blog = None
        if post_id:
            try:
                blog = BlogPost.objects.get(id=post_id)
            except Exception:
                return self.send_response(0, {'error': 'Blog does not exist.'})
        if not blog:
            try:
                blog = BlogPost.objects.create(title=data['title'])
            except Exception:
                return self.send_response(0, {'error': 'Title cannot be empty'})
        if 'products' in data:
            product_ids = data['products']
            BlogProduct.objects.filter(blog=blog).exclude(item__in=product_ids).delete()
            for id in product_ids:
                product = ApprovedProduct.ap_objects.get(id=id)
                BlogProduct.objects.get_or_create(item=product, blog=blog)
        if 'category' in data:
            if data['category'] != "" and not unicode(data['category']).isdigit():
                category = BlogCategory.objects.get(slug=data['category'])
                data['category'] = category.id
        srlzr = BlogPostSrlzr(blog, data=data, context={'post': blog.id})
        if not srlzr.is_valid():
            return self.send_response(0, {'error': srlzr.errors[srlzr.errors.keys()[0]]})
        try:
            srlzr.save()
        except Exception as e:
            return self.send_response(0, e.message)
        response_data = srlzr.data
        # response_data['blog_id'] = srlzr.data['id']
        # response_data['message'] = "Blog post added Successfully"

        # b64_list = []
        # if settings.CELERY_USE:
        #     saveImage.delay(b64_list)
        # else:
        #     saveImage(b64_list)
        # saveImage(b64_list)
        return self.send_response(1, response_data)
        # return self.send_response(1, "Blog post added Successfully")

    def put(self, request, post_id=None, format=None):
        data = request.data.copy()
        try:
            post = BlogPost.objects.get(id=post_id)
        except BlogPost.DoesNotExist:
            return self.send_response(0, {"error": "Blog Does Not Exist"})
        if 'products' in data:
            product_ids = data['products']
            BlogProduct.objects.filter(blog=post).exclude(item__in=product_ids).delete()
            for id in product_ids:
                product = ApprovedProduct.ap_objects.get(id=id)
                BlogProduct.objects.get_or_create(item=product, blog=post)
        if 'category' in data:
            if data['category'] != "" and not unicode(data['category']).isdigit():
                category = BlogCategory.objects.get(slug=data['category'])
                data['category'] = category.id
        if 'status' in data:
            if data['status'] == 'PB':
                data.update({'published_time': timezone.now()})
            if request.user.is_staff:
                data.update({'approved': True})
        srlzr = BlogPostSrlzr(post, data=data, partial=True, context={'post': post.id})
        if not srlzr.is_valid():
            return self.send_response(0, {'error': srlzr.errors[srlzr.errors.keys()[0]]})
        try:
            srlzr.save()
        except Exception as e:
            return self.send_response(0, e.message)
        return self.send_response(1, srlzr.data)


# Retrieve a list of blog post and save a new blog post
class BlogPosts(ZapView):

    # Get a list of all the blogs with the overview
    # Not entire content
    def get(self, request, format=None):
        if request.user.is_authenticated():
            if request.user.is_superuser:
                blogs = BlogPost.objects.all().order_by('-updated_time')
            else:
                blogs = BlogPost.public_objects.all().order_by('-published_time')
        else:
            blogs = BlogPost.public_objects.all().order_by('-published_time')

        page = request.GET.get('page', 1)
        print page

        paginator = Paginator(blogs, 30)
        print paginator.num_pages
        if not paginator.num_pages >= page or page == 0:
            data = {
                'data': [],
                'page': page,
                'total_pages': paginator.num_pages,
                'next': True if page == 0 else False,
                'previous': False if page == 0 else True}

        p = paginator.page(page)
        if request.user.is_authenticated():
            srlzr = BlogListSerializer(p, many=True, context={'user': request.user})
        else:
            srlzr = BlogListSerializer(p, many=True, context={})
        response_data = {'data': srlzr.data, 'page': page, 'total_pages': paginator.num_pages,
                'next': p.has_next(), 'previous': p.has_previous()}

        return self.send_response(1, response_data)

    # Save a Blog Post
    def post(self, request, format=None):
        data = request.data.copy()
        other_data = {}
        try:
            if 'tags' in data:
                other_data['tags'] = data.pop('tags')
            if 'loves' in data:
                other_data['loves'] = data.pop('loves')
            srlzr = BlogPostSrlzr(data=data)
            if not srlzr.is_valid():
                return self.send_response(0, srlzr.errors)
            srlzr.save()
            tags_list = ast.literal_eval(other_data['tags'])
            loves_list = ast.literal_eval(other_data['loves'])
            blog = BlogPost.objects.get(pk=srlzr.data['id'])
            for tag in tags_list:
                blog.tags.add(tag)
            for love in loves_list:
                blog.loves.add(love)
            response_data = {}
            response_data['blog_id'] = srlzr.data['id']
            response_data['message'] = "Blog post added Successfully"
        except Exception as e:
            response_data = {}
            response_data['message'] = str(e)
            return self.send_response(0, {"error": response_data})

        return self.send_response(1, response_data)


# CRUD on individual blog
class SingleBlog(ZapView):

    # Retrieve a specific Blog Post
    def get(self, request, blog_id=None, format=None):
        try:
            blog = BlogPost.objects.get(pk=blog_id)
            print blog
            srlzr = BlogPostSrlzr(data=blog)
            if not srlzr.is_valid():
                return self.send_response(0, srlzr.errors)
            response_data = srlzr.data
            return self.send_response(1, response_data)
        except Exception as e:
            response_data = {}
            response_data['message'] = str(e)
            return self.send_response(0, {"error": response_data})

    # Delete a specific Blog Post
    def delete(self, request, blog_id=None, format=None):
        pass

    # Update a specific Blog Post
    def put(self, request, blog_id=None, format=None):
        pass


# CRUD on blog love
class BlogLove(ZapView):

    # Get all loves on a Blog Post
    def get(self, request, format=None):
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except Exception:
            return self.send_response(0, {'error', 'Blog does not exist.'})
        loved_users = blog.loves.all().values_list('user', flat=True)
        from zap_apps.zapuser.models import ZapUser
        from zap_apps.zapuser.zapuser_serializer import UserSerializer
        users = ZapUser.objects.filter(id__in=loved_users)
        data = UserSerializer(users, many=True).data
        return self.send_response(1, data)

    # Add Love to the Blog Post
    def post(self, request, blog_id, format=None):
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except Exception:
            return self.send_response(0, {'error', 'Blog does not exist.'})
        if request.user.is_authenticated():
            BL.objects.get_or_create(blog_post=blog, user=request.user)
            return self.send_response(1, {'data': 'success'})
        else:
            return self.send_response(0, {'error', 'Please login to post a love.'})

    # Remove Love from the Blog Post
    def delete(self, request, blog_id, format=None):
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except Exception:
            return self.send_response(0, {'error', 'Blog does not exist.'})
        if request.user.is_authenticated():
            try:
                love = BL.objects.get(blog_post=blog, user=request.user)
                love.delete()
                return self.send_response(1, {'data': 'success'})
            except:
                return self.send_response(0, {'error': 'Love not found'})
        else:
            return self.send_response(0, {'error', 'Please login.'})


# Add a subscriber to the blog
class BlogSubscribe(ZapView):

    # Add a subscriber to the blog
    def post(self, request, format=None):
        pass

    # Delete a subscriber from the blog
    def delete(self, request, formt=None):
        pass


# CRUD Blog Tags
class BlogTags(ZapView):

    # Add a new tag
    def post(self, request, format=None):
        pass

    # Retrieve all tags
    def get(self, request, formt=None):
        pass


class BlogCategoryCRUD(AdminRequired, ZapView):

    def get(self, request, format=None):
        categories = BlogCategory.objects.all()
        srlzr = BlogCategorySrlzr(categories, many=True)
        return self.send_response(1, srlzr.data)


class BlogTagCRUD(AdminRequired, ZapView):

    def get(self, request, format=None):
        tags = BlogTag.objects.all()
        srlzr = BlogTagSrlzr(tags, many=True)
        return self.send_response(1, srlzr.data)


class PostData(ZapView):

    def get(self, request, blog_id, format=None):
        data = {}
        if blog_id:
            try:
                blog = BlogPost.objects.get(id=blog_id)
            except Exception:
                return self.send_response(0, {"error": 'Blog does not exist.'})
            srlzr = BlogPostMetaSerializer(blog)
            data.update({'blog_data': srlzr.data})
        categories = BlogCategory.objects.all()
        srlzr = BlogCategorySrlzr(categories, many=True)
        data.update({'categories': srlzr.data})
        authors = Author.objects.all()
        srlzr = AuthorSrlzr(authors, many=True)
        data.update({'authors': srlzr.data})
        tags = BlogTag.objects.all()
        srlzr = BlogTagSrlzr(tags, many=True)
        data.update({'tags': srlzr.data})
        return self.send_response(1, data)


class NextBlog(ZapView):

    def get(self, request, blog_id, format=None):
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except Exception:
            return self.send_response(0, {"error": 'Blog does not exist.'})
        try:
            next_blog = BlogPost.public_objects.filter(published_time__lt=blog.published_time).order_by('-published_time')[0]
            # next_blog = blog.get_next_by_published_time()
            if request.user.is_authenticated():
                srlzr = SingleBlogPostSrlzr(next_blog, context={'user': request.user})
            else:
                srlzr = SingleBlogPostSrlzr(next_blog, context={})
        except Exception:
            return self.send_response(0, {'error': 'End of List'})
        return self.send_response(1, srlzr.data)


class RelatedBlogs(ZapView):

    def get(self, request, product_id, format=None):
        try:
            product = ApprovedProduct.ap_objects.get(id=product_id)
        except Exception:
            return self.send_response(0, {'error': 'Product does not exist'})
        blogs = BlogPost.public_objects.filter(blog_products__item=product).exclude(category__slug='look-book')[0:3]
        looks = BlogPost.public_objects.filter(blog_products__item=product, category__slug='look-book')[0:2]
        if request.user.is_authenticated():
            blog_data = BlogListSerializer(blogs, many=True, context={'user': request.user}).data
            look_data = BlogListSerializer(looks, many=True, context={'user': request.user}).data
        else:
            blog_data = BlogListSerializer(blogs, many=True, context={}).data
            look_data = BlogListSerializer(looks, many=True, context={}).data
        return self.send_response(1, {'blogs': blog_data, 'looks': look_data})

