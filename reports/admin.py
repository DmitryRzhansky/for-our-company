from django.contrib import admin
from django.utils.html import format_html
from .models import WorkReport
from .forms import WorkReportForm


@admin.register(WorkReport)
class WorkReportAdmin(admin.ModelAdmin):
    form = WorkReportForm
    list_display = ('date', 'get_project_name', 'time_spent_hours', 'work_description_short')
    list_filter = ('date', 'created_at', 'project')
    search_fields = ('project_name', 'work_description', 'project__name')
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'project_name', 'project_url', 'date')
        }),
        ('Работа', {
            'fields': ('work_description', 'hours', 'minutes'),
            'description': 'Укажите часы и минуты работы'
        }),
    )
    
    def get_project_name(self, obj):
        """Отображает название проекта в списке"""
        return obj.get_project_name()
    get_project_name.short_description = 'Проект'
    
    def work_description_short(self, obj):
        """Сокращенное описание работы для списка"""
        if len(obj.work_description) > 50:
            return obj.work_description[:50] + '...'
        return obj.work_description
    work_description_short.short_description = 'Описание работы'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()