from django.db import models
from django.urls import reverse


class NewsSource(models.Model):
    """Источник новостей"""
    name = models.CharField(max_length=100, verbose_name="Название")
    url = models.URLField(verbose_name="URL")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    
    class Meta:
        verbose_name = "Источник новостей"
        verbose_name_plural = "Источники новостей"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class News(models.Model):
    """Новость"""
    title = models.CharField(max_length=500, verbose_name="Заголовок")
    url = models.URLField(verbose_name="Ссылка на новость")
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='news', verbose_name="Источник")
    description = models.TextField(blank=True, verbose_name="Описание")
    published_date = models.DateTimeField(verbose_name="Дата публикации")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуемая")
    is_archived = models.BooleanField(default=False, verbose_name="Архивная")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлена")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_date']
        unique_together = ['url', 'source']  # Одна новость из одного источника
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('news:news_detail', kwargs={'pk': self.pk})
    
    @property
    def is_recent(self):
        """Проверяет, является ли новость свежей (за последнюю неделю)"""
        from datetime import timedelta
        from django.utils import timezone
        week_ago = timezone.now() - timedelta(days=7)
        return self.published_date >= week_ago