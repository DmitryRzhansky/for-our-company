from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Project(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'В работе'),
        ('ready', 'Готов'),
        ('archive', 'Архив')
    ]
    
    name = models.CharField(max_length=200, verbose_name='Название проекта')
    project_url = models.URLField(blank=True, verbose_name='URL проекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.CharField(
        choices=STATUS_CHOICES, 
        max_length=20, 
        default='in_progress',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    slug = models.SlugField(unique=True, verbose_name='URL')
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.name


class ProjectContent(models.Model):
    CONTENT_TYPES = [
        ('file', 'Файл'),
        ('html', 'HTML страница'),
        ('text', 'Текстовый блок'),
        ('link', 'Внешняя ссылка'),
        ('image', 'Изображение')
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contents', verbose_name='Проект')
    title = models.CharField(max_length=200, verbose_name='Название')
    content_type = models.CharField(choices=CONTENT_TYPES, max_length=20, verbose_name='Тип контента')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    # Для файлов
    file = models.FileField(upload_to='projects/files/', blank=True, null=True, verbose_name='Файл')
    
    # Для HTML контента
    html_content = models.TextField(blank=True, verbose_name='HTML контент')
    
    # Для текстового контента
    text_content = models.TextField(blank=True, verbose_name='Текстовый контент')
    
    # Для внешних ссылок
    external_url = models.URLField(blank=True, verbose_name='Внешняя ссылка')
    
    # Для изображений
    image = models.ImageField(upload_to='projects/images/', blank=True, null=True, verbose_name='Изображение')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Контент проекта'
        verbose_name_plural = 'Контент проектов'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"