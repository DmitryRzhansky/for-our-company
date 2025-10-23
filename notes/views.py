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
