from django.contrib import admin
from .models import Category, Resource


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fields = ['name', 'description']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'resource_type', 'is_featured', 'is_public', 'created_at']
    list_filter = ['category', 'resource_type', 'is_featured', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'tags']
    list_editable = ['is_featured', 'is_public']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'resource_type')
        }),
        ('Контент', {
            'fields': ('url', 'file', 'image'),
            'description': 'Укажите ссылку или загрузите файл'
        }),
        ('Дополнительно', {
            'fields': ('tags', 'is_featured', 'is_public'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')