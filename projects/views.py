from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, FileResponse
from django.views.generic import ListView, DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
import os
import zipfile
from django.conf import settings
from .models import Project, ProjectContent
from .forms import MultipleFileUploadForm


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Project.objects.all()
        
        # Фильтр по статусу
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        else:
            # По умолчанию показываем только активные проекты
            queryset = queryset.filter(status__in=['in_progress', 'ready'])
        
        # Поиск по названию
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = [
            ('', 'Все статусы'),
            ('in_progress', 'В работе'),
            ('ready', 'Готов'),
            ('archive', 'Архив'),
        ]
        context['current_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Группируем контент по описанию для файлов
        contents = project.contents.all()
        grouped_contents = []
        file_groups = {}
        
        for content in contents:
            if content.content_type == 'file' and content.description:
                # Группируем файлы по описанию
                if content.description not in file_groups:
                    file_groups[content.description] = {
                        'title': content.description,
                        'description': content.description,
                        'files': [],
                        'content_type': 'file_group'
                    }
                file_groups[content.description]['files'].append(content)
            else:
                # Обычный контент
                grouped_contents.append(content)
        
        # Добавляем группы файлов
        for group in file_groups.values():
            grouped_contents.append(group)
        
        context['contents'] = grouped_contents
        return context


def project_download_all(request, slug):
    """Скачать все файлы проекта одним архивом"""
    project = get_object_or_404(Project, slug=slug)
    
    # Создаем временный ZIP файл
    import tempfile
    import io
    
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Добавляем файлы
        for content in project.contents.filter(content_type='file'):
            if content.file:
                file_path = content.file.path
                if os.path.exists(file_path):
                    zip_file.write(file_path, content.file.name)
        
        # Добавляем изображения
        for content in project.contents.filter(content_type='image'):
            if content.image:
                image_path = content.image.path
                if os.path.exists(image_path):
                    zip_file.write(image_path, content.image.name)
    
    zip_buffer.seek(0)
    
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{project.slug}.zip"'
    
    return response


def content_view(request, slug, content_id):
    """Просмотр конкретного контента"""
    project = get_object_or_404(Project, slug=slug)
    content = get_object_or_404(ProjectContent, id=content_id, project=project)
    
    if content.content_type == 'html':
        return render(request, 'projects/content_html.html', {
            'project': project,
            'content': content
        })
    elif content.content_type == 'text':
        return render(request, 'projects/content_text.html', {
            'project': project,
            'content': content
        })
    else:
        raise Http404("Контент не найден")


def content_download(request, slug, content_id):
    """Скачать отдельный файл"""
    project = get_object_or_404(Project, slug=slug)
    content = get_object_or_404(ProjectContent, id=content_id, project=project)
    
    if content.content_type == 'file' and content.file:
        file_path = content.file.path
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{content.title}.{content.file.name.split(".")[-1]}"'
            return response
    
    raise Http404("Файл не найден")


@staff_member_required
def multiple_file_upload(request):
    """Массовая загрузка файлов"""
    if request.method == 'POST':
        form = MultipleFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            created_contents = form.save()
            messages.success(
                request, 
                f'Успешно загружено {len(created_contents)} файлов в проект "{form.cleaned_data["project"].name}"'
            )
            return redirect('admin:projects_projectcontent_changelist')
    else:
        form = MultipleFileUploadForm()
    
    return render(request, 'projects/multiple_file_upload.html', {'form': form})