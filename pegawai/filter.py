import django_filters
from . models import PegawaiModel


class FilterPegawai(django_filters.FilterSet):
    class Meta:
        model = PegawaiModel
        fields = ['nama', 'nip', 'opd_id', 'golongan']