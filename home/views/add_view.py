from .views import *

@login_required
def add_room(request):
    user = request.user

    # Check if the user owns any products
    products = Product.objects.filter(owner=user)
    if not products.exists():
        return redirect('cart')  # Redirect if no owned products
    error = ''
    if request.method == 'POST':
        form = RoomFormCreate(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = user
            room.product = products.first()
            room.save()
            return redirect('cart')  # Redirect to success URL
        else:
            error = 'Có lỗi khi bạn gửi bài. Vui lòng kiểm tra biểu mẫu và thử lại.'
    else:
        # Prepopulate the product field with the user's first product
        initial_product = products.first() if products.exists() else None
        form = RoomFormCreate(initial={'product': initial_product})

    # Fetch the user's profile for the template
    user_profile = get_object_or_404(UserProfile, user=user)

    context = {
        'form': form,
        'profile': user_profile,
        'user_not_login': "none",
        'product': products,
        'error': error
    }

    return render(request, 'apps/add_room.html', context)


@login_required
def add_hotel(request):
    """
    Handle adding a new hotel for authenticated sellers.
    """
    user_profile = UserProfile.objects.get(user=request.user)
    products = Product.objects.filter(owner = request.user)
    
    # Ensure only users with the 'seller' role can access this view
    if user_profile.role != 'seller' or products.exists():
        return redirect('home')
    error = ''
    if request.method == 'POST':
        form = ProductFormCreate(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            # Save the form but assign the current user as the owner
            product = form.save(commit=False)  # Do not save yet
            product.owner = request.user  # Assign owner explicitly
            product.save()

            form.save_m2m() 
            return redirect(reverse_lazy('cart'))
        else:
            error = 'Vui lòng kiểm tra lại thông tin và thử lại.'
    else:
        form = ProductFormCreate()
    
    context = {
        'form': form,
        'page_name': "hotel_detail",
        'user_not_login': "none",  # User is authenticated
        'profile': user_profile,
        'error': error,
    }
    return render(request, 'apps/add_hotel.html', context)
    
@login_required
def add_hotel_user(request):
    """
    Handle adding a new hotel for authenticated sellers.
    """
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Ensure only users with the 'seller' role can access this view
    if user_profile.role != 'admin':
        return redirect('home')
    error = ''
    if request.method == 'POST':
        form = ProductFormCreateUser(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but assign the current user as the owner
            form.save()
            return redirect(reverse_lazy('cart'))
        else:
            error = 'Vui lòng kiểm tra lại thông tin và thử lại.'
    else:
        form = ProductFormCreateUser()
    
    context = {
        'form': form,
        'user_not_login': "none",  # User is authenticated
        'profile': user_profile,
        'error': error,
    }
    return render(request, 'apps/add_hotel.html', context)


def add_account(request):
    # Check if the logged-in user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    user_not_login = "none"
    # Get the current user's profile
    user_profile = UserProfile.objects.get(user=request.user)
    allow = True  # Allow account creation

    # Forms for account creation
    user_form = UserEditForm(request.POST or None)
    profile_form = UserProfileForm(request.POST or None, request.FILES or None)

    # Initialize error variable
    error = ""

    # Handle POST request
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "Cập nhật":
            if user_form.is_valid() and profile_form.is_valid():
                password1 = user_form.cleaned_data.get('password1')
                password2 = user_form.cleaned_data.get('password2')

                if password1 == password2:
                    # Save the User object
                    user = user_form.save(commit=False)
                    user.set_password(password1)  # Hash the password
                    user.save()

                    # Save the UserProfile object
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.base_password = password1
                    profile.save()

                    

                    return redirect('manage_account')  # Redirect after successful creation
                else:
                    error = "Mật khẩu không đúng"
            else:
                error = "Xảy ra lỗi trong lúc nhập dữ liệu"

    # Render the page with forms and context
    context = {
        'profile': user_profile,
        'allow': allow,
        'user_form': user_form,
        'profile_form': profile_form,
        'error': error,
        'user_not_login': user_not_login,
    }
    return render(request, 'apps/edit_profile.html', context)
