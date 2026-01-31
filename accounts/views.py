from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'login.html', {
                'error': 'Username and password required'
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.groups.filter(name='Admin').exists():
                return redirect('admin_dashboard')

            elif user.groups.filter(name='Supervisor').exists():
                return redirect('supervisor_dashboard')

            elif user.groups.filter(name='Student').exists():
                return redirect('student_dashboard')

            else:
                logout(request)
                return render(request, 'login.html', {
                    'error': 'No role assigned to this user'
                })
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def admin_dashboard(request):
    return render(request, 'admin.html')   # ✅ correct template


@login_required
def supervisor_dashboard(request):
    return render(request, 'supervisor.html')  # ✅ correct template


@login_required
def student_dashboard(request):
    return render(request, 'student.html')  # ✅ correct template
