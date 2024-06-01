from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView
from accountss.forms import *
from accountss.models import Custom_user
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse

from django.contrib.auth import update_session_auth_hash

# views.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def redirect_view(request):
    user = request.user
    if user.first_login:
        user.first_login = False
        user.save()
        return redirect(reverse('profile_detail', kwargs={'pk': user.pk}))
    else:
        return redirect(reverse('home'))




class CustomLoginView(LoginView):
    template_name = 'accountss/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.first_login and user.role == 'customer':
            user.first_login = False
            user.save()
            update_session_auth_hash(self.request, user)  # Update the session, because the backend hashes some of the user session data.
            messages.info(self.request, 'Please complete your profile.')
            return reverse_lazy('profile_update', kwargs={'pk': user.pk})
        elif user.role == 'owner':
            return reverse_lazy('admins:admin_dashboard')
        elif user.role == 'admin':
            return reverse_lazy('admin:index')
        elif user.role == 'manager':
            return reverse_lazy('manager_dashboard')
        else:  # default to 'customer'
            return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return super().form_invalid(form)



        
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accountss/signup.html'


def home(request):
    return render(request, 'room/home.html')


from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
    template_name = None



class ProfileDetailView(LoginRequiredMixin,DetailView):
    model = Custom_user
    template_name = 'accountss/profile_detail.html'
    context_object_name = 'profile'
    

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    model = Custom_user
    template_name = 'accountss/profile_update.html'
    fields = ['username','first_name', 'last_name', 'email', 'country', 'city', 'profile_picture', 'phone_number']

    def get_success_url(self):
        user = self.request.user
        user.first_login = False
        return reverse_lazy('profile_detail', kwargs={'pk': self.object.pk})