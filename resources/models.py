from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Категория ресурсов"""
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    color = models.CharField(max_length=7, default="#808080", verbose_name="Цвет", help_text="HEX код цвета")
    icon = models.CharField(max_length=50, default="bi-folder", verbose_name="Иконка", help_text="Bootstrap Icons класс")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Resource(models.Model):
    """Ресурс (статья, видео, инструмент и т.д.)"""
    
    TYPE_CHOICES = [
        ('article', 'Статья'),
        ('video', 'Видео'),
        ('tool', 'Инструмент'),
        ('script', 'Скрипт'),
        ('plugin', 'Плагин'),
        ('bookmark', 'Закладка'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='resources', verbose_name="Категория")
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other', verbose_name="Тип ресурса")
    
    # Ссылки и файлы
    url = models.URLField(blank=True, verbose_name="Ссылка")
    file = models.FileField(upload_to='resources/files/', blank=True, null=True, verbose_name="Файл")
    image = models.ImageField(upload_to='resources/images/', blank=True, null=True, verbose_name="Изображение")
    
    # Дополнительные поля
    tags = models.CharField(max_length=500, blank=True, verbose_name="Теги", help_text="Через запятую")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемый")
    is_public = models.BooleanField(default=True, verbose_name="Публичный")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('resources:resource_detail', kwargs={'pk': self.pk})
    
    @property
    def tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    @property
    def has_content(self):
        """Проверяет, есть ли у ресурса контент (ссылка или файл)"""
        return bool(self.url or self.file)