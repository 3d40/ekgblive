from django import  forms
from django.contrib.auth import authenticate
from django.db.models import fields
from django.db.models.fields import DateField
from django.forms import widgets
from .models import *
from functools import partial


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password')
            if not user.is_active:
                raise forms.ValidationError('This user is not active')
        return super(UserLoginForm, self).clean(*args, **kwargs)
    
class GolonganHistoryForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(GolonganHistoryForm, self).__init__(*args, **kwargs)
        self.fields['nama'].disabled = True,
        self.fields['nomor_sk'].disabled = True
        self.fields['tanggal'].disabled = True
        #self.fields['mk_tahun'].disabled = True
        #self.fields['mk_bulan'].disabled = True


    class Meta:
        model = GolonganHistoryModel
        fields = ['nama','nomor_sk','tanggal','mk_tahun','mk_bulan','tglpenetapan','pejabat']
    
        
class NominatifForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NominatifForm, self).__init__(*args, **kwargs)
        self.fields['pegawai'].disabled = True,
        self.fields['opd'].disabled = True
    
    class Meta:
        model = NominatifxModels
        fields = '__all__'


class PegawaiModelForm(forms.ModelForm):
    class Meta:
        model = PegawaiModel
        fields = '__all__'


class  TundaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TundaForm, self).__init__(*args, **kwargs)
        self.fields['pegawai'].disabled = True
        self.fields['opd'].disabled = True
        self.fields['keterangan'] = forms.CharField(widget=forms.Textarea, required = True)

    class Meta:
        model = NominatifTundaModel
        fields = ['pegawai','opd','keterangan']
        # fields ='__all__'

class JabatanForm(forms.ModelForm):

    class Meta:
        model = PegawaiModel
        fields = ['jenis_jabatan']

class UploadfileForm(forms.ModelForm):
    class Meta:
        model = GolonganHistoryModel
        fields = ['gambar']
