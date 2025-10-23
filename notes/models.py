from django.db import models
from django.utils import timezone
from projects.models import Project


class Note(models.Model):
    """Общие заметки"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')
    is_important = models.BooleanField(default=False, verbose_name='Важная')
    
    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = 'Заметки'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title


class ProjectNote(models.Model):
    """Заметки к проектам"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes', verbose_name='Проект')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')
    is_important = models.BooleanField(default=False, verbose_name='Важная')
    
    class Meta:
        verbose_name = 'Заметка к проекту'
        verbose_name_plural = 'Заметки к проектам'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"


class Checklist(models.Model):
    """Чек-листы"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='checklists', verbose_name='Проект')
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    
    class Meta:
        verbose_name = 'Чек-лист'
        verbose_name_plural = 'Чек-листы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"
    
    @property
    def completed_items(self):
        return self.items.filter(is_completed=True).count()
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def progress_percentage(self):
        if self.total_items == 0:
            return 0
        return int((self.completed_items / self.total_items) * 100)


class ChecklistItem(models.Model):
    """Элементы чек-листа"""
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='items', verbose_name='Чек-лист')
    text = models.CharField(max_length=500, verbose_name='Текст')
    is_completed = models.BooleanField(default=False, verbose_name='Выполнено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Выполнено')
    
    class Meta:
        verbose_name = 'Элемент чек-листа'
        verbose_name_plural = 'Элементы чек-листов'
        ordering = ['created_at']
    
    def __str__(self):
        return self.text
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)
