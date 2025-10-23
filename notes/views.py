from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import models
import json
from .models import Note, ProjectNote, Checklist, ChecklistItem
from projects.models import Project


class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 20
    
    def get_queryset(self):
        return Note.objects.all().order_by('-updated_at')


class ProjectNoteListView(ListView):
    model = ProjectNote
    template_name = 'notes/project_note_list.html'
    context_object_name = 'notes'
    paginate_by = 20
    
    def get_queryset(self):
        return ProjectNote.objects.all().order_by('-updated_at')


def project_detail_enhanced(request, slug):
    """Расширенная страница проекта со статистикой"""
    project = get_object_or_404(Project, slug=slug)
    
    # Статистика отчетов
    from reports.models import WorkReport
    reports = WorkReport.objects.filter(project=project)
    total_reports = reports.count()
    total_time = reports.aggregate(total=models.Sum('time_spent'))['total'] or models.DurationField().default
    
    # Заметки проекта
    project_notes = project.notes.all().order_by('-updated_at')[:5]
    
    # Чек-листы проекта
    checklists = project.checklists.all().order_by('-created_at')
    
    # Последние отчеты
    recent_reports = reports.order_by('-date', '-created_at')[:5]
    
    context = {
        'project': project,
        'total_reports': total_reports,
        'total_time': total_time,
        'project_notes': project_notes,
        'checklists': checklists,
        'recent_reports': recent_reports,
    }
    
    return render(request, 'projects/project_detail_enhanced.html', context)


def project_checklists(request, slug):
    """Страница всех чек-листов проекта"""
    project = get_object_or_404(Project, slug=slug)
    checklists = project.checklists.all().order_by('-created_at')
    
    # Статистика по чек-листам
    total_checklists = checklists.count()
    completed_checklists = 0
    total_items = 0
    completed_items = 0
    
    # Добавляем вычисленные поля для каждого чек-листа
    checklists_with_stats = []
    for checklist in checklists:
        if checklist.progress_percentage == 100:
            completed_checklists += 1
        total_items += checklist.total_items
        completed_items += checklist.completed_items
        
        # Добавляем вычисленные поля
        checklist.remaining_items = checklist.total_items - checklist.completed_items
        checklists_with_stats.append(checklist)
    
    overall_progress = 0
    if total_items > 0:
        overall_progress = round((completed_items / total_items) * 100)
    
    remaining_items = total_items - completed_items
    
    context = {
        'project': project,
        'checklists': checklists_with_stats,
        'total_checklists': total_checklists,
        'completed_checklists': completed_checklists,
        'total_items': total_items,
        'completed_items': completed_items,
        'remaining_items': remaining_items,
        'overall_progress': overall_progress,
    }
    
    return render(request, 'notes/project_checklists.html', context)


def checklist_detail(request, checklist_id):
    """Детальная страница чек-листа"""
    checklist = get_object_or_404(Checklist, id=checklist_id)
    
    # Разделяем элементы на выполненные и невыполненные
    completed_items = checklist.items.filter(is_completed=True)
    pending_items = checklist.items.filter(is_completed=False)
    
    context = {
        'checklist': checklist,
        'completed_items': completed_items,
        'pending_items': pending_items,
    }
    
    return render(request, 'notes/checklist_detail.html', context)


@require_POST
def toggle_checklist_item(request, item_id):
    """Переключение статуса элемента чек-листа"""
    item = get_object_or_404(ChecklistItem, id=item_id)
    item.is_completed = not item.is_completed
    item.save()
    
    return JsonResponse({
        'success': True,
        'is_completed': item.is_completed,
        'completed_at': item.completed_at.isoformat() if item.completed_at else None
    })


@require_POST
def add_checklist_item(request, checklist_id):
    """Добавление нового элемента в чек-лист"""
    checklist = get_object_or_404(Checklist, id=checklist_id)
    text = request.POST.get('text', '').strip()
    
    if text:
        item = ChecklistItem.objects.create(
            checklist=checklist,
            text=text
        )
        return JsonResponse({
            'success': True,
            'item_id': item.id,
            'text': item.text
        })
    
    return JsonResponse({'success': False, 'error': 'Текст не может быть пустым'})
