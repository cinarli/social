from django.shortcuts import render,redirect
from .models import Profile,Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.db.models import Q
# Create your views here.
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    confirm = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True
            
    context = {
        'profile': profile,
        'form': form,
        'confirm':confirm,
    }
    return render(request, 'profiles/myprofile.html', context=context)
def invites_received_view(request):
    profile = Profile.objects.get(user=request.user) 
    qs = Relationship.objects.invatations_received(profile)
    context = {
        'qs':qs
    }
    return render(request, 'profiles/my_invites.html', context=context)



def invite_profiles_list_view(request):
    user=request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)
    context = {
        'qs':qs
    }
    return render(request, 'profiles/to_intive_list.html', context=context)

def profiles_list_view(request):
    user=request.user
    qs = Profile.objects.get_all_profiles(user)
    context = {
        'qs':qs
    }
    return render(request, 'profiles/profile_list.html', context=context)

class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    # context_object_name = 'qs' 
    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        # profile=Profile.objects.get(user__username__iexact=self.request.user)
        # context["profile"] = profile
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
             rel_receiver.append(item.receiver.user)

        for item in rel_s:
             rel_sender.append(item.sender.user)
        context['rel_receiver'] = rel_receiver
        context['rel_sender'] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True
            
        return context

def send_invatation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        
        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')

def remove_from_friends(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my-profile-view')
    