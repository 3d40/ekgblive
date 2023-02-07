from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserLoginForm
from django.contrib.auth import (
    authenticate,
    login,
    logout)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
import csv, io
from .models import *
import urllib, json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from . forms import *
import datetime
from dateutil.relativedelta import *
from django.core.exceptions import MultipleObjectsReturned
from itertools import zip_longest

def tmtcpns(func):
    pegawai = PegawaiModel.objects.filter(opd_id = opdakses)
    jumlah = len(pegawai)
    #cari TMT_CPNS
    for x in pegawai :
        tahun = int(x.nip[8:12])
        bulan = int(x.nip[12:14])
        tanggal = 1
        cpns = datetime.date(tahun,bulan,tanggal)
        print(cpns)
        q = get_object_or_404(PegawaiModel, id = x.id)
        q.tmt_cpns = cpns
        q.save()
    return render(request, 'pegawai/index.html', {'pegawai':pegawai})