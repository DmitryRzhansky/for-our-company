from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Website(models.Model):
    """Веб-сайт для анализа"""
    url = models.URLField(verbose_name="URL сайта")
    name = models.CharField(max_length=200, verbose_name="Название сайта")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_competitor = models.BooleanField(default=False, verbose_name="Конкурент")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    
    class Meta:
        verbose_name = "Веб-сайт"
        verbose_name_plural = "Веб-сайты"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name or self.url
    
    def get_absolute_url(self):
        return reverse('tools:website_detail', kwargs={'pk': self.pk})


class BasicAnalysis(models.Model):
    """Базовый SEO-анализ страницы"""
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='analyses', verbose_name="Сайт")
    page_url = models.URLField(verbose_name="URL страницы")
    page_title = models.CharField(max_length=500, blank=True, verbose_name="Title")
    
    # Мета-теги
    meta_description = models.TextField(blank=True, verbose_name="Meta Description")
    meta_keywords = models.TextField(blank=True, verbose_name="Meta Keywords")
    meta_robots = models.CharField(max_length=200, blank=True, verbose_name="Meta Robots")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical URL")
    
    # Заголовки
    h1_tags = models.JSONField(default=list, verbose_name="H1 теги")
    h2_tags = models.JSONField(default=list, verbose_name="H2 теги")
    h3_tags = models.JSONField(default=list, verbose_name="H3 теги")
    h4_tags = models.JSONField(default=list, verbose_name="H4 теги")
    h5_tags = models.JSONField(default=list, verbose_name="H5 теги")
    h6_tags = models.JSONField(default=list, verbose_name="H6 теги")
    
    # Open Graph
    og_title = models.CharField(max_length=500, blank=True, verbose_name="OG Title")
    og_description = models.TextField(blank=True, verbose_name="OG Description")
    og_image = models.URLField(blank=True, verbose_name="OG Image")
    og_type = models.CharField(max_length=100, blank=True, verbose_name="OG Type")
    
    # Twitter Cards
    twitter_title = models.CharField(max_length=500, blank=True, verbose_name="Twitter Title")
    twitter_description = models.TextField(blank=True, verbose_name="Twitter Description")
    twitter_image = models.URLField(blank=True, verbose_name="Twitter Image")
    twitter_card = models.CharField(max_length=100, blank=True, verbose_name="Twitter Card")
    
    # Техническая информация
    response_time = models.FloatField(null=True, blank=True, verbose_name="Время ответа (сек)")
    page_size = models.IntegerField(null=True, blank=True, verbose_name="Размер страницы (байт)")
    status_code = models.IntegerField(null=True, blank=True, verbose_name="HTTP статус")
    
    # Файлы
    robots_txt = models.TextField(blank=True, verbose_name="robots.txt")
    sitemap_xml = models.TextField(blank=True, verbose_name="sitemap.xml")
    
    # SEO проблемы
    seo_issues = models.JSONField(default=list, verbose_name="SEO проблемы")
    
    # Простые метрики
    word_count = models.IntegerField(default=0, verbose_name="Количество слов")
    title_length = models.IntegerField(default=0, verbose_name="Длина title")
    description_length = models.IntegerField(default=0, verbose_name="Длина description")
    internal_links = models.IntegerField(default=0, verbose_name="Внутренние ссылки")
    external_links = models.IntegerField(default=0, verbose_name="Внешние ссылки")
    total_links = models.IntegerField(default=0, verbose_name="Всего ссылок")
    extracted_text = models.TextField(blank=True, verbose_name="Извлеченный текст")
    keyword_analysis = models.JSONField(default=dict, verbose_name="Анализ ключевых слов")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    
    class Meta:
        verbose_name = "Базовый анализ"
        verbose_name_plural = "Базовые анализы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.website.name} - {self.page_url}"
    
    def get_absolute_url(self):
        return reverse('tools:analysis_detail', kwargs={'pk': self.pk})
    
    @property
    def has_seo_issues(self):
        """Проверяет, есть ли SEO проблемы"""
        return len(self.seo_issues) > 0
    
    @property
    def total_headings(self):
        """Общее количество заголовков"""
        return (len(self.h1_tags) + len(self.h2_tags) + len(self.h3_tags) + 
                len(self.h4_tags) + len(self.h5_tags) + len(self.h6_tags))
    
    @property
    def has_meta_description(self):
        """Проверяет наличие meta description"""
        return bool(self.meta_description.strip())
    
    @property
    def has_title(self):
        """Проверяет наличие title"""
        return bool(self.page_title.strip())


class SEOIssue(models.Model):
    """SEO проблема"""
    SEVERITY_CHOICES = [
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
        ('critical', 'Критическая'),
    ]
    
    CATEGORY_CHOICES = [
        ('meta', 'Мета-теги'),
        ('content', 'Контент'),
        ('technical', 'Техническая'),
        ('structure', 'Структура'),
        ('performance', 'Производительность'),
    ]
    
    analysis = models.ForeignKey(BasicAnalysis, on_delete=models.CASCADE, related_name='issues', verbose_name="Анализ")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name="Критичность")
    title = models.CharField(max_length=200, verbose_name="Название проблемы")
    description = models.TextField(verbose_name="Описание")
    recommendation = models.TextField(verbose_name="Рекомендация")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    
    class Meta:
        verbose_name = "SEO проблема"
        verbose_name_plural = "SEO проблемы"
        ordering = ['-severity', 'category']
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"



