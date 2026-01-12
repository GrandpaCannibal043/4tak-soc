from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):

    PROJECT_TYPE_CHOICES = [
        ('web', 'Webová aplikácia'),
        ('physical', 'Fyzická práca'),
    ]

    DIFFICULTY_CHOICES = [
        (1, 'Veľmi ľahká'),
        (2, 'Ľahká'),
        (3, 'Stredná'),
        (4, 'Ťažká'),
        (5, 'Veľmi ťažká'),
    ]

    title = models.CharField(max_length=200)
    functionality = models.TextField()
    project_type = models.CharField(max_length=10, choices=PROJECT_TYPE_CHOICES)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=False)


    def __str__(self):
        return self.title
    
class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.project.title} – {self.value}"

class ProjectEdit(models.Model):
    original_project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="edits"
    )

    title = models.CharField(max_length=200)
    functionality = models.TextField()
    project_type = models.CharField(
        max_length=10,
        choices=Project.PROJECT_TYPE_CHOICES
    )
    difficulty = models.IntegerField(
        choices=Project.DIFFICULTY_CHOICES
    )
    image = models.ImageField(
        upload_to='projects/',
        blank=True,
        null=True
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Edit návrh – {self.original_project.title}"
