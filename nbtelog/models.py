from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    social_media_links = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class NewsCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "News Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class News(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    featured_image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "News"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Institution(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    established_date = models.DateField()
    accreditation_status = models.CharField(max_length=50)
    last_audit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Program(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField()
    duration = models.CharField(max_length=50)
    qualification_type = models.CharField(max_length=100)
    accreditation_status = models.CharField(max_length=50)

    class Meta:
        unique_together = ['institution', 'code']

    def __str__(self):
        return f"{self.name} at {self.institution.name}"

class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class SliderImage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='slider_images/')
    caption = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

class ChatBot(models.Model):
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('general', 'General Information'),
        ('accreditation', 'Accreditation'),
        ('programs', 'Programs'),
        ('institutions', 'Institutions'),
        ('admission', 'Admission'),
        ('contact', 'Contact Information')
    ])
    keywords = models.TextField(help_text="Comma-separated keywords for matching")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'question']

    def __str__(self):
        return f"{self.category}: {self.question[:50]}"
