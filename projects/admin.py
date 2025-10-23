from django.contrib import admin
from .models import Project, ProjectContent


class ProjectContentInline(admin.StackedInline):
    model = ProjectContent
    extra = 1
    fields = ('title', 'content_type', 'description', 'file', 'html_content', 'text_content', 'external_url', 'image', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_url', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'project_url')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProjectContentInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'project_url', 'description', 'status')
        }),
        ('URL', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectContent)
class ProjectContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('title', 'project__name')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'title', 'content_type', 'description', 'order')
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