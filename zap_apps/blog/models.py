from django.db import models
from zap_apps.zap_catalogue.thumbs import ImageWithThumbsField
from django.utils import timezone
from django.contrib.auth.models import User
import os

STATUS = (
    ('DR', 'Draft'),
    ('PB', 'Published')
)


class BloggersMeetUpRegistration(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=50, unique=True)
    city = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name + " " + self.email


class BlogCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def set_slug(self):
        return self.name.lower().replace(" ", "-")

    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(BlogCategory, self).save(*args, **kwargs)


class BlogTag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def set_slug(self):
        return self.name.lower().replace(" ", "-")

    def save(self, *args, **kwargs):
        self.slug = self.set_slug()
        super(BlogTag, self).save(*args, **kwargs)


class CustomManager(models.Manager):
    def get_queryset(self):
        return super(CustomManager, self).get_queryset()


class PublicPostManager(models.Manager):
    def get_queryset(self):
        return super(PublicPostManager, self).get_queryset().filter(status='PB', approved=True)


class BlogPost(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        'blog.Author', blank=True, null=True, related_name="blog_post", on_delete=models.SET_NULL)
    category = models.ForeignKey(
        'blog.BlogCategory', blank=True, null=True, related_name="blog_post")
    tags = models.ManyToManyField(
        'blog.BlogTag', blank=True)
    cover_pic = models.CharField(max_length=100, null=True, blank=True)
    preview = models.TextField(null=True, blank=True)
    status = models.CharField(choices=STATUS, default='DR', max_length=2)
    approved = models.BooleanField(default=False)
    published_time = models.DateTimeField(default=timezone.now)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    objects = CustomManager()
    public_objects = PublicPostManager()

    def __unicode__(self):
        return self.title

    @property
    def slug(self):
        return self.title.lower().replace(' ', '-')

    @property
    def cover_pic_thumb(self):
        if self.cover_pic:
            filename, file_extension = os.path.splitext(self.cover_pic)
            if file_extension != '.gif':
                return filename + '.thumb.jpg'
            else:
                return self.cover_pic
        else:
            return self.cover_pic

    @property
    def cover_pic_small(self):
        if self.cover_pic:
            filename, file_extension = os.path.splitext(self.cover_pic)
            if file_extension != '.gif':
                return filename + '.small.jpg'
            else:
                return self.cover_pic
        else:
            return self.cover_pic

    @property
    def cover_pic_medium(self):
        if self.cover_pic:
            filename, file_extension = os.path.splitext(self.cover_pic)
            if file_extension != '.gif':
                return filename + '.medium.jpg'
            else:
                return self.cover_pic
        else:
            return self.cover_pic


    @property
    def cover_pic_large(self):
        if self.cover_pic:
            filename, file_extension = os.path.splitext(self.cover_pic)
            if file_extension != '.gif':
                return filename + '.large.jpg'
            else:
                return self.cover_pic
        else:
            return self.cover_pic

    @property
    def time(self):
        time = self.published_time
        timediff = timezone.now() - time
        if timediff.days > 30:
            return str(timediff.days/30) + ' month ago'
        elif timediff.days == 30:
            return '1 month ago'
        elif timediff.days > 7:
            return str(timediff.days/7) + ' weeks ago'
        elif timediff.days == 7:
            return '1 week ago'
        elif timediff.days > 1:
            return str(timediff.days) + ' days ago'
        elif timediff.days == 1:
            return 'Yesterday'
        else:
            return 'Today'

    class Meta:
        ordering = ['-published_time']


class BlogProduct(models.Model):
    item = models.ForeignKey('zap_catalogue.ApprovedProduct', related_name='look_item')
    alternatives = models.ManyToManyField('zap_catalogue.ApprovedProduct', blank=True, related_name='possible_looks')
    blog = models.ForeignKey(BlogPost, related_name='blog_products')

    def __unicode__(self):
        return str(self.item)


class BlogLove(models.Model):
    blog_post = models.ForeignKey('blog.BlogPost', related_name='loves')
    user = models.ForeignKey('zapuser.ZapUser', blank=True, null=True)
    device = models.CharField(max_length=20, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.blog_post)

    class Meta:
        unique_together = (('blog_post', 'user'), ('blog_post', 'device'))


class BlogComment(models.Model):
    blog_post = models.ForeignKey(
        'blog.BlogPost', related_name='comments_got')
    commented_by = models.ForeignKey('zapuser.ZapUser', null=True, blank=True, related_name='blog_comment')
    comment = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.comment

    class Meta:
        ordering = ['-comment_time']


class Author(models.Model):
    user = models.ForeignKey('zapuser.ZapUser')
    description = models.TextField()
    profile_pic = ImageWithThumbsField("Image", upload_to="uploads/author/",
                                       blank=True, null=True, sizes=())

    def __unicode__(self):
        return self.user.first_name + ' ' + self.user.last_name

    @property
    def name(self):
        return self.user.first_name + ' ' + self.user.last_name


class Subscriber(models.Model):
    email = models.CharField(max_length=100)
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.email