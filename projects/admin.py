from django.contrib import admin
from .models import Project, ProjectEdit, Rating
from .models import Profile, RegistrationCode


# =========================
# SPOLOČNÝ ADMIN MIXIN (CSS)
# =========================
class AdminStyleMixin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("admin/custom_admin.css",)
        }


# =========================
# PROJECT
# =========================
@admin.register(Project)
class ProjectAdmin(AdminStyleMixin):
    list_display = ('title', 'author', 'approved', 'created_at')
    list_filter = ('approved', 'project_type', 'difficulty')
    search_fields = ('title', 'author__username')


# =========================
# PROJECT EDIT
# =========================
@admin.register(ProjectEdit)
class ProjectEditAdmin(AdminStyleMixin):
    list_display = (
        'original_project',
        'author',
        'approved',
        'created_at',
    )
    list_filter = ('approved',)
    search_fields = (
        'original_project__title',
        'author__username',
    )

    def save_model(self, request, obj, form, change):
        """
        Ak admin schváli úpravu projektu (approved=True),
        prepíšu sa údaje do pôvodného projektu.
        """
        super().save_model(request, obj, form, change)

        if obj.approved:
            project = obj.original_project

            project.title = obj.title
            project.functionality = obj.functionality
            project.project_type = obj.project_type
            project.difficulty = obj.difficulty

            if obj.image:
                project.image = obj.image

            project.save()


# =========================
# RATING
# =========================
@admin.register(Rating)
class RatingAdmin(AdminStyleMixin):
    list_display = ('project', 'user', 'value', 'created_at')
    list_filter = ('value',)
    search_fields = ('project__title', 'user__username')

    admin.site.register(Profile)
    admin.site.register(RegistrationCode)