import sys
import os
from datetime import datetime, timedelta
from django.utils import timezone

# Добавляем корневую директорию в путь для импорта parser.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import NewsParser
from .models import News, NewsSource


class NewsParserService:
    """Сервис для парсинга и сохранения новостей"""
    
    def __init__(self):
        self.parser = NewsParser()
        self.sources_mapping = {
            'seonews.ru': 'seonews.ru',
            'vc.ru': 'vc.ru',
            'journal.topvisor.com': 'journal.topvisor.com',
            'habr.com': 'habr.com',
            'seofaqt.ru': 'seofaqt.ru',
            'tools.pixelplus.ru': 'tools.pixelplus.ru'
        }
    
    def get_or_create_source(self, source_name):
        """Получает или создает источник новостей"""
        source, created = NewsSource.objects.get_or_create(
            name=source_name,
            defaults={
                'url': f'https://{source_name}',
                'is_active': True
            }
        )
        return source
    
    def parse_all_sources(self):
        """Парсит все источники и сохраняет новости"""
        # Получаем новости от парсера
        parsed_news = self.parser.parse_all_sources()
        
        added_count = 0
        total_count = len(parsed_news)
        
        for news_data in parsed_news:
            try:
                # Получаем источник
                source_name = news_data.get('source', '')
                source = self.get_or_create_source(source_name)
                
                # Проверяем, не существует ли уже такая новость
                existing_news = News.objects.filter(
                    url=news_data['url'],
                    source=source
                ).first()
                
                if existing_news:
                    continue
                
                # Создаем новую новость
                from django.utils import timezone
                published_date = news_data['date']
                if published_date.tzinfo is None:
                    published_date = timezone.make_aware(published_date)
                
                News.objects.create(
                    title=news_data['title'],
                    url=news_data['url'],
                    source=source,
                    published_date=published_date,
                    description=''  # Парсер не возвращает описание
                )
                added_count += 1
                
            except Exception as e:
                print(f"Ошибка при сохранении новости: {e}")
                continue
        
        return {
            'added': added_count,
            'total': total_count
        }
    
    def cleanup_old_news(self, days=30):
        """Архивирует старые новости"""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_news = News.objects.filter(
            published_date__lt=cutoff_date,
            is_archived=False
        )
        
        archived_count = old_news.update(is_archived=True)
        return archived_count
