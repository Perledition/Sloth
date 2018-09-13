
from rest_framework import serializers
from todo.models import Task

class TodoSerializers(serializers.ModelSerializer): # forms.ModelForm
    class Meta:
        model = Task
        fields = [
            'pk',
            'project',
            'task_title',
            'task_explain',
            'task_imp',
            'task_dead',
            'task_eff',
            'complete',
            'task_start',
            #'task_end ',
        ]
        #read_only_fields = ['pk', 'user', 'project'] #können über die Api nicht geändert werden
        # converts to JSON
        #validation for data passed