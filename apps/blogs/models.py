import uuid
from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

from apps.accounts.models.models import User


# Create your models here.

class BlogCategory(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class Blog(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name="blog_categories")

    image = models.ImageField(upload_to="blogs")
    exerpt = HTMLField()
    content = HTMLField()
    tags = models.TextField(blank=True)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="blog_author")

    published_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:6]}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}"

