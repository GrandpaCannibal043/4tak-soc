from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.db.models import Avg

from .models import Project, Rating, ProjectEdit
from .forms import ProjectForm


# =========================
# HLAVNÁ STRÁNKA (INDEX)
# =========================
def index(request):
    projects = Project.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'projects/index.html', {
        'projects': projects
    })


# =========================
# ZOZNAM PROJEKTOV + FILTRE + STRÁNKOVANIE
# =========================
def project_list(request):
    projects = Project.objects.filter(approved=True)

    project_type = request.GET.get('type')
    difficulty = request.GET.get('difficulty')

    if project_type:
        projects = projects.filter(project_type=project_type)

    if difficulty:
        projects = projects.filter(difficulty=difficulty)

    projects = projects.order_by('-created_at')

    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'projects/project_list.html', {
        'projects': page_obj,
        'page_obj': page_obj,
        'selected_type': project_type,
        'selected_difficulty': difficulty,
    })


# =========================
# DETAIL PROJEKTU + HODNOTENIE
# =========================
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, approved=True)

    # uloženie / aktualizácia hodnotenia
    if request.method == "POST":
        value = int(request.POST.get("rating"))

        Rating.objects.update_or_create(
            project=project,
            user=request.user,
            defaults={"value": value}
        )

        return redirect('project_detail', pk=project.pk)

    average_rating = project.ratings.aggregate(avg=Avg('value'))['avg']

    user_rating = Rating.objects.filter(
        project=project,
        user=request.user
    ).first()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'average_rating': average_rating,
        'user_rating': user_rating,
    })


# =========================
# PRIDANIE PROJEKTU
# =========================
@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            project.approved = False  # čaká na admina
            project.save()
            return render(request, 'projects/project_pending.html')
    else:
        form = ProjectForm()

    return render(request, 'projects/add_project.html', {
        'form': form
    })


# =========================
# ÚPRAVA PROJEKTU (VYTVORÍ EDIT)
# =========================
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, author=request.user)

    if request.method == "POST":
        ProjectEdit.objects.create(
            original_project=project,
            title=request.POST.get("title"),
            functionality=request.POST.get("functionality"),
            project_type=request.POST.get("project_type"),
            difficulty=request.POST.get("difficulty"),
            image=request.FILES.get("image"),
            author=request.user,
            approved=False
        )
        return render(request, "projects/project_pending.html")

    return render(request, "projects/project_edit.html", {
        "project": project
    })


# =========================
# MOJE PROJEKTY
# =========================
@login_required
def my_projects(request):
    approved_projects = Project.objects.filter(
        author=request.user,
        approved=True
    )

    pending_projects = Project.objects.filter(
        author=request.user,
        approved=False
    )

    pending_edits = ProjectEdit.objects.filter(
        author=request.user,
        approved=False
    )

    return render(request, 'projects/my_projects.html', {
        'approved_projects': approved_projects,
        'pending_projects': pending_projects,
        'pending_edits': pending_edits,
    })



# =========================
# REGISTRÁCIA
# =========================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
    else:
        form = UserCreationForm()

    for field in form.fields.values():
        field.widget.attrs.update({
            'class': 'form-control'
        })

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('index')

    return render(request, 'projects/register.html', {
        'form': form
    })


# =========================
# PRIHLÁSENIE
# =========================
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
    else:
        form = AuthenticationForm()

    for field in form.fields.values():
        field.widget.attrs.update({
            'class': 'form-control'
        })

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('index')

    return render(request, 'projects/login.html', {
        'form': form
    })



# =========================
# ODHLÁSENIE
# =========================
def logout_view(request):
    logout(request)
    return redirect('index')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def approve_project_edit(request, edit_id):
    edit = get_object_or_404(ProjectEdit, id=edit_id, approved=False)
    project = edit.original_project

    if request.method == "POST":
        # prepíš pôvodný projekt
        project.title = edit.title
        project.functionality = edit.functionality
        project.project_type = edit.project_type
        project.difficulty = edit.difficulty

        if edit.image:
            project.image = edit.image

        project.save()

        # označ editáciu ako schválenú
        edit.approved = True
        edit.save()

        return redirect("admin_project_edits")

    return render(request, "projects/admin_approve_edit.html", {
        "edit": edit,
        "project": project,
    })

@staff_member_required
def admin_project_edits(request):
    edits = ProjectEdit.objects.filter(approved=False).order_by("-created_at")
    return render(request, "projects/admin_project_edits.html", {
        "edits": edits
    })