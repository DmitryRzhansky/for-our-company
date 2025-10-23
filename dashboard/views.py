from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from projects.models import Project
from reports.models import WorkReport


def dashboard(request):
    """Главная страница с общей статистикой"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Статистика проектов
    projects_stats = {
        'total': Project.objects.count(),
        'in_progress': Project.objects.filter(status='in_progress').count(),
        'ready': Project.objects.filter(status='ready').count(),
        'archive': Project.objects.filter(status='archive').count(),
    }
    
    # Статистика отчетов
    reports_stats = {
        'today_time': WorkReport.objects.filter(date=today).aggregate(
            total=Sum('time_spent')
        )['total'] or timedelta(),
        'week_time': WorkReport.objects.filter(date__gte=week_ago).aggregate(
            total=Sum('time_spent')
        )['total'] or timedelta(),
        'month_time': WorkReport.objects.filter(date__gte=month_ago).aggregate(
            total=Sum('time_spent')
        )['total'] or timedelta(),
        'total_reports': WorkReport.objects.count(),
    }
    
    # Последние проекты
    recent_projects = Project.objects.filter(
        status__in=['in_progress', 'ready']
    ).order_by('-created_at')[:5]
    
    # Последние отчеты
    recent_reports = WorkReport.objects.order_by('-date', '-created_at')[:10]
    
    # Отчеты за сегодня
    today_reports = WorkReport.objects.filter(date=today).order_by('-created_at')
    
    context = {
        'projects_stats': projects_stats,
        'reports_stats': reports_stats,
        'recent_projects': recent_projects,
        'recent_reports': recent_reports,
        'today_reports': today_reports,
        'today': today,
    }
    
    return render(request, 'dashboard/dashboard.html', context)