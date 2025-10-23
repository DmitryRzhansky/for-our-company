from django.db import models
from django.utils import timezone


class WorkReport(models.Model):
    project_name = models.CharField(max_length=200, verbose_name='Название проекта')
    project_url = models.URLField(blank=True, verbose_name='Ссылка на проект')
    work_description = models.TextField(verbose_name='Описание работы')
    time_spent = models.DurationField(verbose_name='Потрачено времени')
    date = models.DateField(default=timezone.now, verbose_name='Дата')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Отчет о работе'
        verbose_name_plural = 'Отчеты о работе'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.date} - {self.project_name} ({self.time_spent})"
    
    @property
    def time_spent_hours(self):
        """Возвращает время в часах для отображения"""
        total_seconds = self.time_spent.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        if hours > 0:
            return f"{hours}ч {minutes}м"
        else:
            return f"{minutes}м"