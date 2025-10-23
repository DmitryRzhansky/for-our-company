from django.core.management.base import BaseCommand
from news.parser_service import NewsParserService


class Command(BaseCommand):
    help = 'Парсит новости из всех источников'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Архивировать старые новости (старше 30 дней)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Начинаем парсинг новостей...')
        
        try:
            parser_service = NewsParserService()
            result = parser_service.parse_all_sources()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Парсинг завершен! Добавлено {result["added"]} новых новостей из {result["total"]} найденных.'
                )
            )
            
            if options['cleanup']:
                archived_count = parser_service.cleanup_old_news()
                self.stdout.write(
                    self.style.SUCCESS(f'Архивировано {archived_count} старых новостей.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при парсинге: {str(e)}')
            )
