from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):

    PROJECT_TYPE_CHOICES = [
        ('web', 'Webová aplikácia'),
        ('physical', 'Fyzická práca'),
    ]

    DIFFICULTY_CHOICES = [
        ('Veľmi ľahká', 'Veľmi ľahká'),
        ('Ľahká', 'Ľahká'),
        ('Stredná', 'Stredná'),
        ('Ťažká', 'Ťažká'),
        ('Veľmi ťažká', 'Veľmi ťažká'),
    ]

    CLASS_CHOICES = [
        ('4AT', '4AT'),
        ('4AS', '4AS'),
        ('4AM', '4AM'),
        ('4AI', '4AI'),
        ('4BI', '4BI'),
        ('4CI', '4CI'),
        ('4AE', '4AE'),
        ('3AT', '3AT'),
        ('3AS', '3AS'),
        ('3AM', '3AM'),
        ('3AI', '3AI'),
        ('3BI', '3BI'),
        ('3CI', '3CI'),
        ('3AE', '3AE'),
    ]

    title = models.CharField(max_length=200)

    # POPIS PROJEKTU – ponechaný
    functionality = models.TextField()

    project_type = models.CharField(
        max_length=10,
        choices=PROJECT_TYPE_CHOICES
    )

    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES
    )

    school_class = models.CharField(
        max_length=3,
        choices=CLASS_CHOICES,
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='projects/images/',
        blank=True,
        null=True
    )

    # PDF SOČ dokumentácia
    documentation_pdf = models.FileField(
        upload_to='projects/pdfs/',
        blank=True,
        null=True
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Rating(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
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

    # POPIS PROJEKTU – ponechaný
    functionality = models.TextField()

    project_type = models.CharField(
        max_length=10,
        choices=Project.PROJECT_TYPE_CHOICES
    )

    difficulty = models.IntegerField(
        choices=Project.DIFFICULTY_CHOICES
    )

    school_class = models.CharField(
        max_length=3,
        choices=Project.CLASS_CHOICES
    )

    image = models.ImageField(
        upload_to='projects/images/',
        blank=True,
        null=True
    )

    documentation_pdf = models.FileField(
        upload_to='projects/pdfs/',
        blank=True,
        null=True
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Edit návrh – {self.original_project.title}"
