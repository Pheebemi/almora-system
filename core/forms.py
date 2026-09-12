from django import forms
from django.forms import ModelForm
from .models import Applicant, ScreeningForm, ProgramChoice
from accounts.models import User, Faculty, Department
from accounts.state import NIGERIA_STATES_AND_LGAS
from datetime import datetime   

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ApplicantForm(ModelForm):
    user = UserForm()
    class Meta:
        model = Applicant
        fields = ['user', 'state', 'phone_number', 'programs', 'mode']

class ApplicantScreeningForm(ModelForm):
    sex = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')],
        required=True,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    state_of_origin = forms.ChoiceField(
        choices=[(state, state) for state in NIGERIA_STATES_AND_LGAS.keys()],
        required=True,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    local_government = forms.ChoiceField(
        choices=[],  # Initially empty, populated dynamically
        required=True,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    middle_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    surname = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        required=True
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    contact_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 3}),
        required=True
    )    
    jamb_reg_no = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    jamb_score = forms.CharField(
        max_length=3,
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )

    # School Information Fields
    primary_school = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter primary school name'
        })
    )
    primary_school_dates = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '2012-2018'
        })
    )
    secondary_school = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter secondary school name'
        })
    )
    secondary_school_dates = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': '2018-2024'
        })
    )

    first_choice = forms.ModelChoiceField(
        queryset=None,  # Will be set dynamically
        required=True,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    second_choice = forms.ModelChoiceField(
        queryset=None,  # Will be set dynamically
        required=False,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    third_choice = forms.ModelChoiceField(
        queryset=None,  # Will be set dynamically
        required=True,
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    waec_result = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    jamb_result_slip = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    birth_certificate = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    passport_photo = forms.FileField(
        required=True, 
        widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'})
    )
    declaration = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'})
    )
    
    def __init__(self, *args, **kwargs):
        applicant = kwargs.pop('applicant', None)
        super().__init__(*args, **kwargs)

        # Populate LGA choices based on the selected state
        if 'state_of_origin' in self.data:
            state = self.data.get('state_of_origin')
            if state in NIGERIA_STATES_AND_LGAS:
                self.fields['local_government'].choices = [(lga, lga) for lga in NIGERIA_STATES_AND_LGAS[state]]
        elif self.instance and self.instance.state_of_origin:
            state = self.instance.state_of_origin
            if state in NIGERIA_STATES_AND_LGAS:
                self.fields['local_government'].choices = [(lga, lga) for lga in NIGERIA_STATES_AND_LGAS[state]]

        # Set dynamic program choices based on applicant's program type
        if applicant:
            program_type = applicant.programs.program_type
            choices_queryset = ProgramChoice.objects.filter(
                program_type=program_type,
                is_active=True
            )

            self.fields['first_choice'].queryset = choices_queryset
            self.fields['second_choice'].queryset = choices_queryset
            self.fields['third_choice'].queryset = choices_queryset
        else:
            # Default empty queryset if no applicant provided
            empty_queryset = ProgramChoice.objects.none()
            self.fields['first_choice'].queryset = empty_queryset
            self.fields['second_choice'].queryset = empty_queryset
            self.fields['third_choice'].queryset = empty_queryset

        # Make file fields not required based on verification status
        if self.instance and self.instance.pk:
            # Only require re-upload for rejected documents
            # Verified or pending documents don't need re-upload
            if self.instance.waec_result and self.instance.waec_result_status != 'rejected':
                self.fields['waec_result'].required = False
            if self.instance.jamb_result_slip and self.instance.jamb_result_slip_status != 'rejected':
                self.fields['jamb_result_slip'].required = False
            if self.instance.passport_photo and self.instance.passport_photo_status != 'rejected':
                self.fields['passport_photo'].required = False

            # Clear 'N/A' default values to show placeholder text
            if self.instance.primary_school == 'N/A':
                self.initial['primary_school'] = ''
            if self.instance.primary_school_dates == 'N/A':
                self.initial['primary_school_dates'] = ''
            if self.instance.secondary_school == 'N/A':
                self.initial['secondary_school'] = ''
            if self.instance.secondary_school_dates == 'N/A':
                self.initial['secondary_school_dates'] = ''

    def clean(self):
        cleaned_data = super().clean()
        state = cleaned_data.get('state_of_origin')
        lga = cleaned_data.get('local_government')

        # Validate LGA belongs to the selected state
        if state and lga:
            if state in NIGERIA_STATES_AND_LGAS:
                if lga not in NIGERIA_STATES_AND_LGAS[state]:
                    self.add_error('local_government', 'Invalid LGA for the selected state.')

        # Validate course choices are unique
        first_choice = cleaned_data.get('first_choice')
        second_choice = cleaned_data.get('second_choice')
        third_choice = cleaned_data.get('third_choice')

        choices = [first_choice, second_choice, third_choice]
        choices = [c for c in choices if c is not None]  # Remove None values
        if len(set(choices)) != len(choices):
            self.add_error(None, 'Course choices must be different.')

        return cleaned_data

    class Meta:
        model = ScreeningForm
        fields = '__all__'
        exclude = [
            'applicant',
            'created_at',
            'courses',
            # Exclude verification fields (admin-only)
            'waec_result_status',
            'waec_result_comment',
            'jamb_result_slip_status',
            'jamb_result_slip_comment',
            'passport_photo_status',
            'passport_photo_comment',
            'birth_certificate_status',
            'birth_certificate_comment',
            'verified_by',
            'verified_at',
        ]