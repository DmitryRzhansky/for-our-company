from django.contrib import admin
from .models import Note, ProjectNote, Checklist, ChecklistItem


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_important', 'created_at', 'updated_at')
    list_filter = ('is_important', 'created_at')
    search_fields = ('title', 'content')
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'is_important')
        }),
    )


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1
    fields = ('text', 'is_completed')


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'progress_display', 'created_at')
    list_filter = ('project', 'created_at')
    search_fields = ('title', 'description', 'project__name')
    inlines = [ChecklistItemInline]
    
    def progress_display(self, obj):
        return f"{obj.completed_items}/{obj.total_items} ({obj.progress_percentage}%)"
    progress_display.short_description = 'Прогресс'


@admin.register(ProjectNote)
class ProjectNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'is_important', 'created_at', 'updated_at')
    list_filter = ('project', 'is_important', 'created_at')
    search_fields = ('title', 'content', 'project__name')
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('project', 'title', 'content', 'is_important')
        }),
    )


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'checklist', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'checklist__project', 'created_at')
    search_fields = ('text', 'checklist__title')
    ordering = ['checklist', 'created_at']
