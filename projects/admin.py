from django.contrib import admin
from .models import Project, ProjectContent


class ProjectContentInline(admin.TabularInline):
    model = ProjectContent
    extra = 1
    fields = ('title', 'content_type', 'description', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'client')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProjectContentInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'client', 'description', 'status')
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
        ('Контент', {
            'fields': ('file', 'html_content', 'text_content', 'external_url', 'image'),
            'classes': ('collapse',)
        }),
    )