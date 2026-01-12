from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'approved', 'created_at')
    list_filter = ('approved', 'project_type', 'difficulty')
    search_fields = ('title', 'author__username')
