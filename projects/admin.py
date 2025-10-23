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
            'classes': ('collapse',),
            'description': 'Для загрузки нескольких файлов используйте <a href="/projects/upload-multiple/" target="_blank">массовую загрузку</a>'
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
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['mass_upload_link'] = '/projects/upload-multiple/'
        return super().changelist_view(request, extra_context=extra_context)

