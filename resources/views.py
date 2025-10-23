from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Category, Resource


class ResourceListView(ListView):
    """Список всех ресурсов"""
    model = Resource
    template_name = 'resources/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Resource.objects.filter(is_public=True).select_related('category')
        
        # Фильтрация по категории
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Фильтрация по типу
        resource_type = self.request.GET.get('type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        # Фильтрация по тегам
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        # Поиск
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['title', '-title', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['resource_types'] = Resource.TYPE_CHOICES
        context['featured_resources'] = Resource.objects.filter(is_featured=True, is_public=True)[:6]
        
        # Получаем все уникальные теги
        all_tags = set()
        for resource in Resource.objects.filter(is_public=True):
            all_tags.update(resource.tags_list)
        context['all_tags'] = sorted(list(all_tags))
        
        return context


class ResourceDetailView(DetailView):
    """Детальная страница ресурса"""
    model = Resource
    template_name = 'resources/resource_detail.html'
    context_object_name = 'resource'
    
    def get_queryset(self):
        return Resource.objects.filter(is_public=True).select_related('category')


class CategoryListView(ListView):
    """Список категорий"""
    model = Category
    template_name = 'resources/category_list.html'
    context_object_name = 'categories'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем количество ресурсов для каждой категории
        for category in context['categories']:
            category.resource_count = Resource.objects.filter(category=category, is_public=True).count()
        return context


class CategoryDetailView(DetailView):
    """Ресурсы конкретной категории"""
    model = Category
    template_name = 'resources/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resources = Resource.objects.filter(
            category=self.object, 
            is_public=True
        ).select_related('category')
        
        # Фильтрация по типу
        resource_type = self.request.GET.get('type')
        if resource_type:
            resources = resources.filter(resource_type=resource_type)
        
        # Поиск
        search = self.request.GET.get('search')
        if search:
            resources = resources.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        context['resources'] = resources.order_by('-created_at')
        context['resource_types'] = Resource.TYPE_CHOICES
        return context