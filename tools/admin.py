from django.contrib import admin
from .models import Website, BasicAnalysis, SEOIssue


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_competitor', 'created_at']
    list_filter = ['is_competitor', 'created_at']
    search_fields = ['name', 'url', 'description']
    ordering = ['-created_at']


@admin.register(BasicAnalysis)
class BasicAnalysisAdmin(admin.ModelAdmin):
    list_display = ['website', 'page_url', 'page_title', 'status_code', 'has_seo_issues', 'created_at']
    list_filter = ['website', 'status_code', 'created_at']
    search_fields = ['page_url', 'page_title', 'meta_description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('website', 'page_url', 'page_title')
        }),
        ('Мета-теги', {
            'fields': ('meta_description', 'meta_keywords', 'meta_robots', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('Заголовки', {
            'fields': ('h1_tags', 'h2_tags', 'h3_tags', 'h4_tags', 'h5_tags', 'h6_tags'),
            'classes': ('collapse',)
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image', 'og_type'),
            'classes': ('collapse',)
        }),
        ('Twitter Cards', {
            'fields': ('twitter_title', 'twitter_description', 'twitter_image', 'twitter_card'),
            'classes': ('collapse',)
        }),
        ('Техническая информация', {
            'fields': ('response_time', 'page_size', 'status_code'),
            'classes': ('collapse',)
        }),
        ('Файлы', {
            'fields': ('robots_txt', 'sitemap_xml'),
            'classes': ('collapse',)
        }),
        ('SEO проблемы', {
            'fields': ('seo_issues',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SEOIssue)
class SEOIssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'analysis', 'category', 'severity', 'created_at']
    list_filter = ['category', 'severity', 'created_at']
    search_fields = ['title', 'description', 'recommendation']
    ordering = ['-severity', 'category']

