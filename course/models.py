from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Topic(models.Model):
    title = models.CharField(max_length=100, help_text='输入课题名称')
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title

class Course(models.Model):
    owner = models.ForeignKey(User, related_name="courses_created", on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic, related_name="courses")
    title = models.CharField(max_length=100, help_text='输入课程名称')
    slug = models.SlugField(max_length=100, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='course_enrolled', blank=True)

    class Meta:
        ordering = ['-created', 'title']
    
    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=100, help_text='输入模块名词')
    description = models.TextField()

    class Meta:
        ordering = ['course']

    def __str__(self):
        return '{}. {}'.format(self.course, self.title)

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Content(models.Model):
    module = models.ForeignKey(Module, related_name="contents", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in':(
                                                                                            'Text', 
                                                                                            'File',
                                                                                            'Image',
                                                                                            'Video')})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        ordering = ['module']

from django.template.loader import render_to_string

class Text(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name="TextItems", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField()
    
    def __str__(self):
        return self.title

    def render(self):
        return render_to_string('course/content/text.html', {'item': self})

class File(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name="FileItems", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='files')
    
    def __str__(self):
        return self.title

    def render(self):
        return render_to_string('course/content/file.html', {'item': self})

class Image(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name="ImageItems", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to='images')
    
    def __str__(self):
        return self.title

    def render(self):
        return render_to_string('course/content/image.html', {'item': self})

class Video(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name="VideoItems", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    url = models.URLField()
    
    def __str__(self):
        return self.title

    def render(self):
        return render_to_string('course/content/video.html', {'item': self})
