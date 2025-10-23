from django.core.management.base import BaseCommand
from django.utils.text import slugify
from projects.models import Project


class Command(BaseCommand):
    help = 'Исправляет пустые slug у проектов'

    def handle(self, *args, **options):
        # Находим все проекты с пустыми slug
        projects_with_empty_slug = Project.objects.filter(slug='')
        
        self.stdout.write(f'Найдено проектов с пустыми slug: {projects_with_empty_slug.count()}')
        
        for project in projects_with_empty_slug:
            old_slug = project.slug
            project.slug = slugify(project.name)
            project.save()
            self.stdout.write(
                self.style.SUCCESS(f'Исправлен проект: "{project.name}" -> slug: "{project.slug}"')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Исправлено {projects_with_empty_slug.count()} проектов!')
        )
