from django.contrib import admin
from .models import UserProfile, NewsCategory, News, Institution, Program, Document, SliderImage, ChatBot

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    search_fields = ['user__username', 'phone_number']

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'created_at', 'category']
    list_filter = ['status', 'created_at', 'category']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'accreditation_status', 'established_date']
    list_filter = ['accreditation_status']
    search_fields = ['name', 'code']

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution', 'code', 'qualification_type', 'accreditation_status']
    list_filter = ['qualification_type', 'accreditation_status', 'institution']
    search_fields = ['name', 'code', 'institution__name']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title', 'description')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)

@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'caption')
    ordering = ('order', '-created_at')

@admin.register(ChatBot)
class ChatBotAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer', 'keywords')
