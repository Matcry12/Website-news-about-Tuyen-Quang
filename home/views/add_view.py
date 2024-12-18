from .views import *

class AddRoomView(CreateView):
    model = Room
    form_class = RoomFormCreate
    template_name = 'apps/add_room.html'
    success_url = reverse_lazy('cart')

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login if not authenticated

        # Check if the user owns any products
        products = Product.objects.filter(owner=request.user)
        if not products.exists():  # If the user has no products
            return redirect('cart')  # Redirect to the cart page

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        products = Product.objects.filter(owner=user)

        if products.exists():
            kwargs['initial'] = {'product': products.first()}
        else:
            kwargs['initial'] = {'product': None}
        
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        selected_product = form.cleaned_data['product']
        products = Product.objects.filter(owner=user)

        # Validate that the selected product belongs to the user
        if selected_product not in products:
            form.add_error('product', 'Bạn không thể chọn cơ sở lưu trú không phải của mình.')
            return self.form_invalid(form)

        # Proceed to save the room if validation passes
        room = form.save(commit=False)
        room.owner = user
        room.save()

        return super().form_valid(form)
    def form_invalid(self, form):
        storage = get_messages(request)
        for message in storage:
            pass  # Iterating through storage clears it
        
        messages.error(self.request, "Có lỗi khi bạn gửi bài. Vui lòng kiểm tra biểu mẫu và thử lại.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=self.request.user)
            products = Product.objects.filter(owner=self.request.user)
            context['profile'] = user_profile
            context['user_not_login'] = "none"
            context['product'] = products
        else:
            context['user_not_login'] = "block"
            context['profile'] = None
            context['product'] = None

        return context


class AddHotelView(CreateView):
    model = Product
    form_class = ProductFormCreate  # Use your custom form if necessary
    template_name = 'apps/add_hotel.html'
    success_url = reverse_lazy('cart')

    def form_valid(self, form):
        user_profile = UserProfile.objects.get(user=self.request.user)

        # Ensure the user is a seller (you can adjust this logic based on your app)
        if user_profile.role != 'seller':
            # Redirect to home or show a forbidden message if the user is not a seller
            return redirect('home')

        # Automatically assign the owner to the logged-in user
        product = form.save(commit=False)
        product.owner = self.request.user
        product.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        # Redirect unauthenticated users before reaching the view
        if not request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        # Prepare context data for template
        context = super().get_context_data(**kwargs)

        # Add additional context
        context['page_name'] = "hotel_detail"
        context['user_not_login'] = "none"  # Since user is authenticated at this point
        return context
    


class AddAccountView(TemplateView):
    template_name = 'apps/edit_profile.html'
    user_form_class = UserEditForm
    profile_form_class = UserProfileForm
    success_url = reverse_lazy('manage_account')

    def get(self, request, *args, **kwargs):
        # Provide empty forms on GET request
        user_form = self.user_form_class()
        profile_form = self.profile_form_class()
        allow = True
        user_profile = UserProfile.objects.get(user = request.user)
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'allow': allow,
            'profile': user_profile,
        })

    def post(self, request, *args, **kwargs):
        # Instantiate forms with POST data and files (for profile image)
        user_form = self.user_form_class(request.POST)
        profile_form = self.profile_form_class(request.POST, request.FILES)
        user_profile = UserProfile.objects.get(user = request.user)
        if user_form.is_valid() and profile_form.is_valid():
            # Save the User model
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password1'])  # Securely set the password
            user.save()

            # Link and save the UserProfile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            return redirect(self.success_url)
        else:
            # Re-render with errors
            return render(request, self.template_name, {
                'user_form': user_form,
                'profile_form': profile_form,
                'profile': user_profile,
            })
