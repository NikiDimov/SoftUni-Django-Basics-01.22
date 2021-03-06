import datetime

from django import forms
from django.core.exceptions import ValidationError

from petstagram.main_app.models import Profile, Pet, PetPhoto


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'profile_picture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter URL'}),
        }


class CreatePetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = ('name', 'type', 'date_of_birth')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pet name'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.SelectDateWidget(
                attrs={'class': 'form-control'},
                years=range(1920, datetime.datetime.now().year + 1)),
        }

    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        exclude.remove('user_profile')  # allow checking against the missing attribute

        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e.message_dict)


class CreatePhotoForm(forms.ModelForm):
    class Meta:
        model = PetPhoto
        fields = ('photo', 'description', 'tagged_pets')
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder': 'Enter description.',
                                                 'rows': 3}),
            'tagged_pets': forms.SelectMultiple(attrs={'class': 'form-control'})
        }


class EditPhotoForm(forms.ModelForm):
    class Meta:
        model = PetPhoto
        fields = ('description', 'tagged_pets')
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'tagged_pets': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class EditPetForm(CreatePetForm):
    pass


class DeletePetForm(CreatePetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.disabled = True


class EditProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['gender'] = 'Do not show'

    class Meta:
        model = Profile
        fields = "__all__"
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.SelectDateWidget(attrs={'class': 'form-control'},
                                                    years=range(1920, datetime.datetime.now().year)),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3})

        }


class DeleteProfileForm(forms.ModelForm):
    def save(self, commit=True):
        pets = list(self.instance.pet_set.all())
        PetPhoto.objects.filter(tagged_pets__in=pets).delete()
        self.instance.delete()
        return self.instance

    class Meta:
        model = Profile
        fields = ()
