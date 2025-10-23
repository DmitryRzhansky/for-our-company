from django import forms
from django.core.exceptions import ValidationError
from .models import WorkReport


class WorkReportForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=23, required=False, initial=0, label='Часы')
    minutes = forms.IntegerField(min_value=0, max_value=59, required=False, initial=0, label='Минуты')
    
    class Meta:
        model = WorkReport
        fields = ['project_name', 'project_url', 'work_description', 'date']
        widgets = {
            'work_description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если редактируем существующий отчет, заполняем часы и минуты
        if self.instance and self.instance.pk and self.instance.time_spent:
            total_seconds = self.instance.time_spent.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            self.fields['hours'].initial = hours
            self.fields['minutes'].initial = minutes
    
    def clean(self):
        cleaned_data = super().clean()
        hours = cleaned_data.get('hours', 0) or 0
        minutes = cleaned_data.get('minutes', 0) or 0
        
        if hours == 0 and minutes == 0:
            raise ValidationError('Время не может быть нулевым. Укажите хотя бы 1 минуту.')
        
        # Создаем timedelta из часов и минут
        from datetime import timedelta
        cleaned_data['time_spent'] = timedelta(hours=hours, minutes=minutes)
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.time_spent = self.cleaned_data['time_spent']
        if commit:
            instance.save()
        return instance
