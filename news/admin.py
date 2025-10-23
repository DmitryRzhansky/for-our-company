from django.contrib import admin
from .models import NewsSource, News


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'url']
    ordering = ['name']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'source', 'published_date', 'is_featured', 'is_archived', 'created_at']
    list_filter = ['source', 'is_featured', 'is_archived', 'published_date', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_featured', 'is_archived']
    ordering = ['-published_date']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'url', 'source', 'description')
        }),
        ('Даты', {
            'fields': ('published_date',)
        }),
        ('Настройки', {
            'fields': ('is_featured', 'is_archived'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('source')