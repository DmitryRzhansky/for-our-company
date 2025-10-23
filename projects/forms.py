from django import forms
from .models import ProjectContent


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class MultipleFileUploadForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=None,
        label='Проект',
        help_text='Выберите проект для загрузки файлов'
    )
    files = MultipleFileField(
        label='Файлы',
        help_text='Выберите несколько файлов (удерживайте Ctrl для выбора нескольких)'
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Описание',
        required=False,
        help_text='Общее описание для всех файлов'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Project
        self.fields['project'].queryset = Project.objects.all()
    
    def save(self):
        project = self.cleaned_data['project']
        files = self.cleaned_data['files']
        description = self.cleaned_data['description']
        
        # Если files - это список файлов
        if isinstance(files, list):
            file_list = files
        else:
            file_list = [files]
        
        created_contents = []
        for file in file_list:
            content = ProjectContent.objects.create(
                project=project,
                title=file.name,
                content_type='file',
                description=description,
                file=file
            )
            created_contents.append(content)
        
        return created_contents
