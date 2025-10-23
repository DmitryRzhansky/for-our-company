from django.views.generic import ListView
from django.db.models import Q
from .models import News, NewsSource


class NewsListView(ListView):
    """Список всех новостей"""
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = News.objects.filter(is_archived=False).select_related('source')
        
        # Фильтрация по источнику
        source_id = self.request.GET.get('source')
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        
        # Поиск
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(source__name__icontains=search)
            )
        
        # Фильтр по рекомендуемым
        featured = self.request.GET.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Фильтр по свежим (за неделю)
        recent = self.request.GET.get('recent')
        if recent == 'true':
            from datetime import timedelta
            from django.utils import timezone
            week_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(published_date__gte=week_ago)
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-published_date')
        if sort_by in ['title', '-title', 'published_date', '-published_date', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = NewsSource.objects.filter(is_active=True)
        context['featured_news'] = News.objects.filter(is_featured=True, is_archived=False)[:6]
        
        # Статистика
        from datetime import timedelta
        from django.utils import timezone
        week_ago = timezone.now() - timedelta(days=7)
        
        context['stats'] = {
            'total_news': News.objects.filter(is_archived=False).count(),
            'recent_news': News.objects.filter(published_date__gte=week_ago, is_archived=False).count(),
            'featured_news': News.objects.filter(is_featured=True, is_archived=False).count(),
        }
        
        return context

