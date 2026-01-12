from django.urls import path
from .views import (
    index,
    project_list,
    project_detail,
    add_project,
    project_edit,
    register,
    login_view,
    logout_view,
    my_projects,
    admin_project_edits,
    approve_project_edit,
)

urlpatterns = [
    path('', index, name='index'),
    path('projects/', project_list, name='project_list'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', project_edit, name='project_edit'),
    path('add/', add_project, name='add_project'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('my-projects/', my_projects, name='my_projects'),
    path('admin/project-edits/', admin_project_edits, name='admin_project_edits'),
    path('admin/project-edits/<int:edit_id>/approve/', approve_project_edit, name='approve_project_edit'),
]
