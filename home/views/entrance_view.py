from .views import *

def loginPage(request):
    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it

    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else: messages.info(request, 'Tài khoản hoặc mật khẩu không đúng!')
    # Check if there are any superusers in the database
    allow = False
    if not User.objects.filter(is_superuser=True).exists():
        # If no superusers exist, allow any user to create a superuser
        allow = True
    context = {'allow': allow}
    return render(request, 'apps/login.html', context)
def logoutPage(request):
    logout(request)
    return redirect('login')

def register(request):
    storage = get_messages(request)
    for message in storage:
        pass  # Iterating through storage clears it

    form = CreationUserForm()
    context = {'form': form}
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = CreationUserForm(request.POST)
        
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(password1)
        print(password2)
        
        if form.is_valid():
            user = form.save()

            UserProfile.objects.create(
                user=user,
                role='customer',  # Default role
                phonecall=request.POST.get('phonecall', 'N/a'),  # Additional fields
                cccd=request.POST.get('cccd', 'N/a'),
                birthday=request.POST.get('birthday'),
                base_password=None,
            )

            return redirect('login')
        else: messages.info(request, 'Đăng ký không phù hợp!')

    return render(request, 'apps/register.html', context)
