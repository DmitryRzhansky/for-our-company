from django.contrib import admin
from .models import Project, ProjectContent


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_url', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'project_url')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'project_url', 'description', 'status')
        }),
    )


@admin.register(ProjectContent)
class ProjectContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('title', 'project__name')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'title', 'content_type', 'description')
        }),
        ('Файл', {
            'fields': ('file',),
            'classes': ('collapse',)
        }),
        ('HTML контент', {
            'fields': ('html_content',),
            'classes': ('collapse',)
        }),
        ('Текстовый контент', {
            'fields': ('text_content',),
            'classes': ('collapse',)
        }),
        ('Внешняя ссылка', {
            'fields': ('external_url',),
            'classes': ('collapse',)
        }),
        ('Изображение', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
    )

