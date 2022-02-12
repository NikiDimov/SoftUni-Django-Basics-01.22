from django.shortcuts import render, redirect

from petstagram.main_app.forms import CreateProfileForm, CreatePetForm, CreatePhotoForm
from petstagram.main_app.models import PetPhoto, Profile, Pet


def get_profile():
    profiles = Profile.objects.all()
    if profiles:
        return profiles[0]
    return None


def show_home(request):
    context = {
        'hide_additional_nav_items': True
    }
    return render(request, 'home_page.html', context)


def show_dashboard(request):
    profile = get_profile()
    if not profile:
        return show_401_error(request)
    pet_photos = set(PetPhoto.objects.prefetch_related('tagged_pets').filter(tagged_pets__user_profile=profile))
    context = {
        'pet_photos': pet_photos
    }
    return render(request, 'dashboard.html', context)


def show_profile(request):
    profile = get_profile()
    if not profile:
        return show_401_error(request)
    pets = Pet.objects.filter(user_profile=profile)
    pet_photos = set(PetPhoto.objects.prefetch_related('tagged_pets').filter(tagged_pets__user_profile=profile))
    total_likes = sum([pet_photo.likes for pet_photo in pet_photos])
    context = {
        'profile': profile,
        'pets': pets,
        'pet_photos': pet_photos,
        'total_likes': total_likes,
    }
    return render(request, 'profile_details.html', context)


def show_pet_photo_details(request, pk):
    profile = get_profile()
    if not profile:
        return show_401_error(request)
    pet_photo = PetPhoto.objects.prefetch_related('tagged_pets').get(pk=pk)
    context = {
        'pet_photo': pet_photo
    }
    return render(request, 'photo_details.html', context)


def like_pet_photo(request, pk):
    pet_photo = PetPhoto.objects.get(pk=pk)
    pet_photo.likes += 1
    pet_photo.save()
    return redirect('photo details', pk)


def show_401_error(request):
    return render(request, '401_error.html')


def create_profile(request):
    if request.method == "POST":
        form = CreateProfileForm(request.POST, instance=Profile())
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CreateProfileForm(instance=Profile())
    context = {'form': form}
    return render(request, 'profile_create.html', context)


def add_pet(request):
    if request.method == 'POST':
        form = CreatePetForm(request.POST, instance=Pet(user_profile=get_profile()))
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CreatePetForm(instance=Pet())
    context = {'form': form}
    return render(request, 'pet_create.html', context)


def add_photo(request):
    if request.method == 'POST':
        form = CreatePhotoForm(request.POST, request.FILES, instance=PetPhoto())
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CreatePhotoForm(instance=PetPhoto())
    context = {'form': form}
    return render(request, 'photo_create.html', context)


def edit_photo(request, pk):
    return render(request, 'photo_edit.html')


def edit_pet(request, pk):
    return render(request, 'pet_edit.html')


def delete_pet(request, pk):
    return render(request, 'pet_delete.html')


def edit_profile(request):
    return render(request, 'profile_edit.html')


def delete_profile(request):
    return render(request, 'profile_delete.html')
