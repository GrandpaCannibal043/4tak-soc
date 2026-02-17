from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.db.models import Avg
from django.contrib.admin.views.decorators import staff_member_required
from .models import Project, Rating, ProjectEdit, ProjectHistory
from .forms import ProjectForm, CustomUserCreationForm
from .utils import generate_unique_code
from .models import RegistrationCode
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect



# =========================
# HLAVNÁ STRÁNKA
# =========================
def index(request):
    projects = Project.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'projects/index.html', {
        'projects': projects
    })


# =========================
# ZOZNAM PROJEKTOV
# =========================
from django.contrib.auth.models import User

def project_list(request):
    projects = Project.objects.filter(approved=True)

    project_type = request.GET.get('type')
    difficulty = request.GET.get('difficulty')
    author = request.GET.get('author')
    school_class = request.GET.get('school_class')
    mentor = request.GET.get('mentor')   # ← PRIDAJ TOTO

    if project_type:
        projects = projects.filter(project_type=project_type)

    if difficulty:
        projects = projects.filter(difficulty=difficulty)

    if author:
        projects = projects.filter(author__username__icontains=author)

    if school_class:
        projects = projects.filter(school_class=school_class)

    if mentor:   # ← PRIDAJ TOTO
        projects = projects.filter(mentor__username__icontains=mentor)

    projects = projects.order_by('-created_at')

    paginator = Paginator(projects, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'projects/project_list.html', {
        'projects': page_obj,
        'page_obj': page_obj,
        'selected_type': project_type,
        'selected_difficulty': difficulty,
        'selected_author': author,
        'selected_class': school_class,
        'selected_mentor': mentor,   # ← PRIDAJ TOTO
        'class_choices': Project.CLASS_CHOICES,
        'teachers': User.objects.filter(profile__role='teacher'),  # ← A TOTO
    })




# =========================
# DETAIL PROJEKTU + HODNOTENIE
# =========================
@login_required
def project_detail(request, pk):

    project = get_object_or_404(Project, pk=pk)

    # 🔒 OCHRANA NESCHVÁLENÝCH PROJEKTOV
    if not project.approved:
        if (
            request.user != project.author and
            request.user != project.mentor and
            request.user.profile.role != 'admin'
        ):
            return redirect('project_list')

    # ⭐ Hodnotenie iba pre schválené projekty
    if request.method == "POST" and project.approved:
        value = int(request.POST.get("rating"))

        Rating.objects.update_or_create(
            project=project,
            user=request.user,
            defaults={"value": value}
        )
        return redirect('project_detail', pk=project.pk)

    average_rating = None
    user_rating = None

    if project.approved:
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

            # Ak je používateľ študent → mentor je povinný
            if request.user.profile.role == 'student' and not form.cleaned_data.get('mentor'):
                form.add_error('mentor', 'Musíš vybrať mentora.')
            else:
                project = form.save(commit=False)
                project.author = request.user
                project.approved = False
                project.save()

                return render(request, 'projects/project_pending.html')

    else:
        form = ProjectForm()

    return render(request, 'projects/add_project.html', {
        'form': form
    })



# =========================
# ÚPRAVA PROJEKTU → VYTVORÍ ProjectEdit
# =========================
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, author=request.user)

    if request.method == "POST":

        # uložiť históriu pred zmenou
        ProjectHistory.objects.create(
            project=project,
            edited_by=request.user,
            old_title=project.title,
            old_functionality=project.functionality,
            old_school_class=project.school_class,
            old_project_type=project.project_type,
            old_difficulty=project.difficulty,
        )

        # teraz prepíš projekt
        project.title = request.POST.get("title")
        project.functionality = request.POST.get("functionality")
        project.school_class = request.POST.get("school_class")
        project.project_type = request.POST.get("project_type")
        project.difficulty = request.POST.get("difficulty")

        if request.FILES.get("image"):
            project.image = request.FILES.get("image")

        if request.FILES.get("documentation_pdf"):
            project.documentation_pdf = request.FILES.get("documentation_pdf")

        project.save()

        return redirect("project_detail", pk=project.pk)

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()

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


# =========================
# ADMIN – SCHVÁLENIE EDITU
# =========================
@login_required
def approve_project_edit(request, edit_id):

    edit = get_object_or_404(ProjectEdit, id=edit_id, approved=False)
    project = edit.original_project

    # Povoliť teacherovi iba ak je mentor
    if request.user.profile.role == "teacher":
        if project.mentor != request.user:
            return redirect("teacher_dashboard")

    # Admin môže všetko
    elif request.user.profile.role != "admin":
        return redirect("project_list")

    if request.method == "POST":

        project.title = edit.title
        project.functionality = edit.functionality
        project.school_class = edit.school_class
        project.project_type = edit.project_type
        project.difficulty = edit.difficulty

        if edit.image:
            project.image = edit.image

        if edit.documentation_pdf:
            project.documentation_pdf = edit.documentation_pdf

        project.save()

        edit.approved = True
        edit.save()

        return redirect("teacher_dashboard")

    return render(request, "projects/approve_edit.html", {
        "edit": edit,
        "project": project,
    })




@staff_member_required
def admin_project_edits(request):
    edits = ProjectEdit.objects.filter(approved=False).order_by("-created_at")
    return render(request, "projects/admin_project_edits.html", {
        "edits": edits
})


@login_required
def generate_code_page(request):
    from .utils import generate_unique_code
    from .models import RegistrationCode, Profile

    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user, role='admin')

    if request.user.profile.role == 'student':
        return redirect('project_list')

    generated_code = None

    if request.method == "POST":

        # Žiacky kód
        if request.POST.get("code_type") == "student":
            if request.user.profile.role in ['admin', 'teacher']:
                code = generate_unique_code(6)
                RegistrationCode.objects.create(
                    code=code,
                    role='student',
                    created_by=request.user
                )
                generated_code = code

        # Učiteľský kód
        if request.POST.get("code_type") == "teacher":
            if request.user.profile.role == 'admin':
                code = generate_unique_code(8)
                RegistrationCode.objects.create(
                    code=code,
                    role='teacher',
                    created_by=request.user
                )
                generated_code = code

    return render(request, 'projects/generate_code_page.html', {
        'generated_code': generated_code
    })

@login_required
def teacher_dashboard(request):

    if request.user.profile.role not in ['teacher', 'admin']:
        return redirect('project_list')

    if request.user.profile.role == 'teacher':

        pending_projects = Project.objects.filter(
            mentor=request.user,
            approved=False
        )

        approved_projects = Project.objects.filter(
            mentor=request.user,
            approved=True
        )

        pending_edits = ProjectEdit.objects.filter(
            original_project__mentor=request.user,
            approved=False
        )

    else:  # admin

        pending_projects = Project.objects.filter(
            approved=False
        )

        approved_projects = Project.objects.filter(
            approved=True
        )

        pending_edits = ProjectEdit.objects.filter(
            approved=False
        )

    return render(request, 'projects/teacher_dashboard.html', {
        'pending_projects': pending_projects,
        'approved_projects': approved_projects,
        'pending_edits': pending_edits,
    })





@login_required
def approve_project(request, pk):
    project = Project.objects.get(pk=pk)

    # Teacher môže schváliť iba svoje mentorované projekty
    if request.user.profile.role == 'teacher':
        if project.mentor != request.user:
            return redirect('project_list')

    # Admin môže schváliť všetko
    elif request.user.profile.role != 'admin':
        return redirect('project_list')

    project.approved = True
    project.save()

    return redirect('teacher_dashboard')

@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if (
        request.user.profile.role != 'admin' and
        request.user != project.mentor
    ):
        return redirect('project_list')

    project.delete()
    return redirect('teacher_dashboard')

@login_required
def project_history(request, pk):

    project = get_object_or_404(Project, pk=pk)

    if request.user.profile.role not in ["teacher", "admin"]:
        return redirect("project_list")

    history = project.history.order_by("-edited_at")

    return render(request, "projects/project_history.html", {
        "project": project,
        "history": history,
    })
