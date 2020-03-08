""" 
    ==============================================================
    | django-thumbs  -  by Antonio Mele (http://django.es)       |
    ==============================================================


    Usage example:
    ==============
    photo = ImageWithThumbsField(upload_to='images', sizes=((125,125),(300,200),)
    
    To retrieve image URL, exactly the same way as with ImageField:
        my_object.photo.url
    To retrieve thumbnails URL's just add the size to it:
        my_object.photo.url_100x100
        my_object.photo.url_300x200
    
    Note: The 'sizes' attribute is not required. If you don't provide it, 
    ImageWithThumbsField will act as a normal ImageField
        
    How it works:
    =============
    For each size in the 'sizes' atribute of the field it generates a 
    thumbnail with that size and stores it following this format:
    
    available_filename.[width]x[height].extension

    Where 'available_filename' is the available filename returned by the storage
    backend for saving the original file.
    
    Following the usage example above: For storing a file called "photo.jpg" it saves:
    photo.jpg          (original file)
    photo.125x125.jpg  (first thumbnail)
    photo.300x200.jpg  (second thumbnail)
    
    With the default storage backend if photo.jpg already exists it will use these filenames:
    photo_.jpg
    photo_.125x125.jpg
    photo_.300x200.jpg
"""

from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile

from PIL import Image
from cStringIO import StringIO


def generate_thumb(img, thumb_size, format):
    img.seek(0)  # see http://code.djangoproject.com/ticket/8222 for details
    image = Image.open(img)

    # Convert to RGB if necessary
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    # get size
    thumb_w, thumb_h = thumb_size
    # If you want to generate a square thumbnail
    if thumb_w == thumb_h:
        # quad
        xsize, ysize = image.size
        # get minimum size
        minsize = min(xsize, ysize)
        # largest square possible in the image
        xnewsize = (xsize - minsize) / 2
        ynewsize = (ysize - minsize) / 2
        # crop it
        image2 = image.crop(
            (xnewsize, ynewsize, xsize - xnewsize, ysize - ynewsize))
        # load is necessary after crop
        image2.load()
        # thumbnail of the cropped image (with ANTIALIAS to make it look
        # better)
        image2.thumbnail(thumb_size, Image.ANTIALIAS)
    else:
        # not quad
        image2 = image
        image2.thumbnail(thumb_size, Image.ANTIALIAS)

    io = StringIO()
    # PNG and GIF are the same, JPG is JPEG
    if format.upper() == 'JPG':
        format = 'JPEG'

    image2.save(io, format)
    return ContentFile(io.getvalue())


class ImageWithThumbsFieldFile(ImageFieldFile):
    """
    See ImageWithThumbsField for usage example
    """

    def __init__(self, *args, **kwargs):
        super(ImageWithThumbsFieldFile, self).__init__(*args, **kwargs)
        self.sizes = self.field.sizes

        if self.sizes:
            def get_size(self, size):
                if not self:
                    return ''
                else:
                    split = self.url.rsplit('.', 1)
                    thumb_url = '%s.%sx%s.%s' % (split[0], w, h, split[1])
                    return thumb_url

            for size in self.sizes:
                (w, h) = size
                setattr(self, 'url_%sx%s' % (w, h), get_size(self, size))

    def save(self, name, content, save=True):
        super(ImageWithThumbsFieldFile, self).save(name, content, save)

        if self.sizes:
            for size in self.sizes:
                (w, h) = size
                split = self.name.rsplit('.', 1)
                thumb_name = '%s.%sx%s.%s' % (split[0], w, h, split[1])

                # you can use another thumbnailing function if you like
                thumb_content = generate_thumb(content, size, split[1])

                thumb_name_ = self.storage.save(thumb_name, thumb_content)

                if not thumb_name == thumb_name_:
                    raise ValueError(
                        'There is already a file named %s' % thumb_name)

    def delete(self, save=True):
        name = self.name
        super(ImageWithThumbsFieldFile, self).delete(save)
        if self.sizes:
            for size in self.sizes:
                (w, h) = size
                split = name.rsplit('.', 1)
                thumb_name = '%s.%sx%s.%s' % (split[0], w, h, split[1])
                try:
                    self.storage.delete(thumb_name)
                except:
                    pass


class ImageWithThumbsField(ImageField):
    attr_class = ImageWithThumbsFieldFile

    def __init__(self, verbose_name=None, name=None, width_field=None,
                 height_field=None, sizes=None, **kwargs):
        self.verbose_name = verbose_name
        self.name = name
        self.width_field = width_field
        self.height_field = height_field
        self.sizes = sizes
        super(ImageField, self).__init__(**kwargs)
