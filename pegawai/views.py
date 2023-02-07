from typing import Dict, get_args
from django.db.models import query
from django.db.models.expressions import Exists, Value, ValueRange
from django.db.models.fields import CharField
from django.db.models.query import InstanceCheckMeta, QuerySet, ValuesListIterable
from django.http.request import QueryDict
from django.http.response import HttpResponse
from django.shortcuts import get_list_or_404, render, get_object_or_404, redirect, HttpResponseRedirect
from django.utils.timezone import now
# from .forms import UserLoginForm
from django.contrib.auth import (
    authenticate,
    login,
    logout)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
import csv
import io
from .models import *
from urllib.request import urlopen
import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView
from . forms import *
import datetime
from dateutil.relativedelta import *
from django.core.exceptions import MultipleObjectsReturned
from itertools import count, zip_longest
from django.http import Http404
from django.views.generic import ListView, DetailView, View, DeleteView
from django.views.generic.detail import SingleObjectMixin
from .filter import FilterPegawai
import os.path
from xhtml2pdf import pisa
from django.template.loader import get_template

from socket import error as SocketError
import errno
import roman
from datetime import date
from django.core import serializers
from django.urls import reverse_lazy, reverse



# Create your views here.

urlpegawai = 'http://103.114.144.202/nip/?search='
urlcompany = 'http://103.114.144.202/nip/?company='
urlpangkat = 'http://103.114.144.202/riwayatpangkat/?search='


def LoginView(request):
    if request.user.is_authenticated:
        return redirect('pegawai:index')
    if request.POST:
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            akun = AkunModel.objects.get(akun=user.id)
            opdakses = request.session['opd_akses'] = akun.jenis_akun
            if user.is_active:
                try:
                    request.session['username'] = request.POST['username']
                    login(request, user)
                    return redirect('pegawai:index')
                except:
                    messages.add_message(request, messages.INFO,'User belum terverifikasi')
        else:
            messages.add_message(request, messages.INFO,'Username atau password Anda salah')
    return render(request, 'registration/login.html')


def LogoutView(request):
    try:
        logout(request)
        del request.session['username']
    except KeyError:
        pass
    return render(request, 'registration/login.html')


@login_required()
def IndexView(request):
    userdata = request.session['username']
    user = User.objects.get(username= userdata)
    opdakses = request.session['opd_akses']
    akun = get_object_or_404(AkunModel, akun_id= user.id )
    opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
    print(list(opdnya))
    if opdakses == 'admin' :
        print(userdata, user.is_active, user.is_staff, user.is_superuser, akun.jenis_akun, akun.opd_akses)
    # if user.is_superuser == True and user.is_staff == True and user.is_active == True :
        pegawai = PegawaiModel.objects.all()
        disetujui = NominatifxModels.objects.all()
        diproses = ProsesBerkalaModel.objects.all()
        finish = NominatifSelesaiModels.objects.all()
        pending = NominatifTundaModel.objects.all()
        jumlah = len(pegawai)
        usulan = len(disetujui)
        selesai = len(finish)
        proses = len(diproses)
        tunda = len(pending)
        context = {'pegawai': pegawai, 'jumlah': jumlah, 'usulan': usulan, 'selesai': selesai, 'proses':proses, 'tunda':tunda}
        return render(request, 'pegawai/dahsboard.html', context)
    elif opdakses == 'operatoropd':
    # elif akun.jenis_akun == 'operatoropd' and user.is_superuser == False and user.is_staff == True and user.is_active == True:
        pegawai = PegawaiModel.objects.filter(opd_id= akun.opd_akses_id)
        disetujui = NominatifxModels.objects.filter(opd = akun.opd_akses_id)
        diproses = ProsesBerkalaModel.objects.filter(opd = akun.opd_akses_id)
        finish = NominatifSelesaiModels.objects.filter(opd = akun.opd_akses_id) 
        pending = NominatifTundaModel.objects.filter(opd = akun.opd_akses_id)
        jumlah = len(pegawai)
        usulan = len(disetujui)
        selesai = len(finish)
        proses = len(diproses)
        tunda = len(pending)
        context = {'pegawai': pegawai, 'jumlah': jumlah, 'usulan': usulan, 'selesai': selesai, 'proses':proses, 'tunda':tunda}
        return render(request, 'pegawai/dahsboard.html', context)
    elif opdakses == 'operator':
    # elif akun.jenis_akun == 'operator' and user.is_superuser == False and user.is_staff == True and user.is_active == True:
        pegawai = PegawaiModel.objects.filter(opd_id__in= list(opdnya))
        disetujui = NominatifxModels.objects.filter(opd__in = list(opdnya))
        diproses = ProsesBerkalaModel.objects.filter(opd__in = list(opdnya))
        finish = NominatifSelesaiModels.objects.filter(opd__in = list(opdnya)) 
        pending = NominatifTundaModel.objects.filter(opd__in = list(opdnya))
        jumlah = len(pegawai)
        usulan = len(disetujui)
        selesai = len(finish)
        proses = len(diproses)
        tunda = len(pending)
        context = {'pegawai': pegawai, 'jumlah': jumlah, 'usulan': usulan, 'selesai': selesai, 'proses':proses, 'tunda':tunda}
        return render(request, 'pegawai/dahsboard.html', context)
    else:
        messages.add_message("anda Tidak Memiliki Account")
    return render(request, 'pegawai/dahsboard.html')

@login_required()
def HitungPangkatView(request, id):
    template_name = 'pegawai/detail.html'
    request.session['username']
    opdakses = request.session['opd_akses']
    pegawai = get_object_or_404(PegawaiModel, id=id)
    jab = get_object_or_404(JabatanModel, id = pegawai.jabatan_id)
    tahun = int(pegawai.nip[0:4])
    bulan = int(pegawai.nip[4:6])
    tanggal = int(pegawai.nip[6:8]) 
    lahir = datetime.date(tahun,bulan,tanggal)
    pegawai.tgllahir = lahir
    pegawai.save()
    context = {
        'pegawai':pegawai,
        'jab':jab
        }  
    print(jab)
    try:
        
        pangkat = urlopen(urlpangkat + str(pegawai.id))
        json_pangkat = json.load(pangkat)
        # print(json_pangkat)
    except SocketError as e:
        print("ada error", e)
        if e.errno != errno.ECONNRESET:
            raise # Not error we are looking for
        pass # Handle error here
    else:
        for pkt in json_pangkat:
            if GolonganHistoryModel.objects.filter(pengguna=pegawai.id, id= pkt['id']).exists():
                    updatenya = GolonganHistoryModel.objects.get(id = pkt['id'])
                    updatenya.id=pkt['id'] 
                    updatenya.pengguna=pkt['partner'] 
                    updatenya.nama_id=pkt['golongan_id_history']
                    updatenya.nip=pegawai.nip
                    updatenya.jenis=pkt['jenis'] 
                    updatenya.tanggal=pkt['date']
                    updatenya.nomor_sk = pkt['name']
                    updatenya.save()
            else:
                GolonganHistoryModel.objects.filter(pengguna=pegawai.id).create(
                    id=pkt['id'],
                    pengguna=pkt['partner'],
                    nama_id=pkt['golongan_id_history'],
                    nip=pegawai.nip,
                    jenis=pkt['jenis'],
                    tanggal=pkt['date'],
                    nomor_sk = pkt['name'],
                )
    return render(request, template_name,context)


def RiwayatPangkatView(request, nip):
    request.session['username']
    opdakses = request.session['opd_akses']
    pangkat = GolonganHistoryModel.objects.filter(nip=nip).order_by('-tanggal')
    pegawai = get_object_or_404(PegawaiModel, nip=nip)
    return render(request, 'pegawai/riwayatpangkat.html', {'object_list': pangkat, 'pegawai': pegawai})


class Pegawai(ListView):
    model = PegawaiModel
    ordering = ['tmt_cpns']
    template_name = 'pegawai/pegawaimodel_list.html'
    paginate_by = 25

    def get_queryset(self,):
        userdata = self.request.session['username']
        user = User.objects.get(username= userdata)
        opdakses = self.request.session['opd_akses']
        akun = get_object_or_404(AkunModel, akun_id= user.id )
        opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
        print(userdata, user.is_active, user.is_staff, user.is_superuser)
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            queryset = PegawaiModel.objects.all()
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
            queryset = PegawaiModel.objects.filter(opd_id =akun.opd_akses_id)
        elif opdakses == 'operator':
            queryset = PegawaiModel.objects.filter(opd_id__in=list(opdnya))

        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset


def CariView(request):
    userdata = request.session['username']
    opdakses = request.session['opd_akses']
    queryset = PegawaiModel.objects.all()
    user = User.objects.get(username= userdata)
    akun = get_object_or_404(AkunModel, akun_id= user.id )
    opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
    cari = request.GET.get('search', '')
    if cari is not None and cari != '':
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            caripegawai = PegawaiModel.objects.filter(nama__icontains=cari)
            return render(request, 'pegawai/caripegawai_list.html', {'object_list': caripegawai})
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True: 
            caripegawai = PegawaiModel.objects.filter(opd_id=akun.opd_akses_id, nama__icontains=cari)
            return render(request, 'pegawai/caripegawai_list.html', {'object_list': caripegawai})
        elif opdakses == 'operator':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True: 
            caripegawai = PegawaiModel.objects.filter(opd_id__in=list(opdnya), nama__icontains=cari)
            return render(request, 'pegawai/caripegawai_list.html', {'object_list': caripegawai})
    else:
        return redirect('pegawai:pegawai')
    return render(request, 'pegawai/caripegawai_list.html', {'object_list': caripegawai})


def NominatifViews(request):
    userdata = request.session['username']
    user = User.objects.get(username= userdata)
    tmtkgb_post = request.POST.get('tmtkgb', {})
    request.session['tmtkgb'] = tmtkgb_post
    opdakses = request.session['opd_akses']
    akun = get_object_or_404(AkunModel, akun_id= user.id )
    opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
    pangkat = GolonganHistoryModel.objects.filter(jenis='cpns')
    # cari TMT_CPNS\
    if request.method == 'POST':
        pegawai = PegawaiModel.objects.filter(opd_id=akun.opd_akses_id)
        jumlah = len(pegawai)
        for x in pegawai:
            tahun = int(x.nip[8:12])
            bulan = int(x.nip[12:14])
            tanggal = 1
            cpns = datetime.date(tahun, bulan, tanggal)
            tmtkgb_date = datetime.datetime.strptime(tmtkgb_post, '%Y-%m-%d').date()
            nominasi = relativedelta(tmtkgb_date, cpns).years % 2 == 0 and relativedelta(tmtkgb_date, cpns).months == 0
            nom = pegawai.get(id=x.id)
            nom.nominasi = nominasi
            nom.tmt_cpns = cpns
            nom.save()
            data = pegawai.filter(nominasi=True)
        return render(request, 'pegawai/daftarnominatif.html', {'data': data, 'tmtkgb_date': tmtkgb_date})
    return render(request, 'pegawai/daftarnominatif.html')


class NominatifList(ListView):
    model = NominatifxModels
    ordering = ['tmt_kgb']
    template_name = 'pegawai/nominatiflist.html'
    paginate_by = 25

    def get_queryset(self):
        userdata = self.request.session['username']
        user = User.objects.get(username= userdata)
        opdakses = self.request.session['opd_akses']
        akun = get_object_or_404(AkunModel, akun_id= user.id )
        opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
        print(userdata, user.is_active, user.is_staff, user.is_superuser)
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            queryset = NominatifxModels.objects.all()
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
            queryset = NominatifxModels.objects.filter(opd_id =akun.opd_akses_id)
        elif opdakses == 'operator':
            queryset = NominatifxModels.objects.filter(opd_id__in=list(opdnya))
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset


def NominatifDetailView(request, id):
    request.session['username']
    opdakses = request.session['opd_akses']
    data = get_object_or_404(PegawaiModel, id=id)
    gol = get_object_or_404(GolonganModel, id =data.golongan_id)
    print(data.nama, data.golongan_id)
    pangkat = GolonganHistoryModel.objects.filter(pengguna=data.id, nama=data.golongan).first()
    # pangkat = get_object_or_404(GolonganHistoryModel, pengguna=data.id, nama=data.golongan)
    nominatif = get_object_or_404(NominatifxModels, pegawai_id=data.id)
    gaji = get_object_or_404(GajiModel, id=nominatif.gaji_id)
    return render(request, "pegawai/detailnominatif.html", {'pangkat': pangkat,  'data': data, 'nom': nominatif, 'gaji': gaji})


def CetakPdfFile(request, id):
    request.session['username']
    opdakses = request.session['opd_akses']
    template_path = 'pegawai/cetakpdf.html'
    pegawai = get_object_or_404(PegawaiModel, id=id)
    pangkat = GolonganHistoryModel.objects.filter( nama_id=pegawai.golongan, pengguna=pegawai.id).first()
    simbol = get_object_or_404(GolonganModel, id=pegawai.golongan_id)
    nominatif = get_object_or_404(ProsesBerkalaModel, pegawai_id=pegawai.id)
    gajibaru = get_object_or_404(GajiModel, golongan_id=pegawai.golongan, masa_kerja=nominatif.mkb_tahun)
    gajilama = get_object_or_404(GajiModel, golongan_id=pegawai.golongan, masa_kerja=nominatif.mk_tahun)
    opd = get_object_or_404(OpdModel, id=pegawai.opd_id)
    kgbnext = nominatif.tmt_kgb+relativedelta(years=+2)
    inputselesai = NominatifSelesaiModels.objects.update_or_create(
        golongan_id=nominatif.golongan_id,
        gaji_id=nominatif.gaji_id,
        jabatan=nominatif.jabatan,
        mk_tahun=nominatif.mk_tahun,
        mk_bulan=nominatif.mk_bulan,
        mkb_tahun=nominatif.mkb_tahun,
        mkb_bulan=nominatif.mkb_bulan,
        pegawai_id=nominatif.pegawai_id,
        opd_id=nominatif.opd_id,
        tmt_kgb=nominatif.tmt_kgb,
    )
    inputhistory = GolonganHistoryModel.objects.get_or_create(
        pengguna = pegawai.id,
        nip = pegawai.nip,
        nama_id = pegawai.golongan_id,
        jenis = "sk_kgb",
        tanggal = nominatif.tmt_kgb,
        mk_tahun = nominatif.mkb_tahun,
        mk_bulan = nominatif.mkb_bulan,
        tglpenetapan = nominatif.tanggal
    )
    nominatif.delete()
    # kepelaopd = get_object_or_404(PegawaiModel, id=opd.kepala_opd)
    context = {
        'nominatif': nominatif, 
        'data': pegawai, 
        'pangkat': pangkat,
        'gajibaru': gajibaru, 
        'gajilama': gajilama, 
        'kgbnext': kgbnext, 
        'simbol': simbol}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def Hitungmasakerja(request, id):
    request.session['username']
    opdakses = request.session['opd_akses']
    pangkat = get_object_or_404(GolonganHistoryModel, id=id)
    data = get_object_or_404(PegawaiModel, nip=pangkat.nip)
    golonganall = GolonganHistoryModel.objects.filter(pengguna=data.id).order_by('-tanggal')
    cpnscek = get_object_or_404(GolonganHistoryModel, pengguna=data.id, jenis="cpns")
    pnscek = get_object_or_404(GolonganHistoryModel, pengguna=data.id, jenis="pns")
    pangkatgolongan = get_object_or_404(GolonganHistoryModel, pengguna=data.id, id=id)
    golongandasarfilter = GolonganHistoryModel.objects.filter(pengguna=data.id, jenis="pangkat_golongan")
    for i in golonganall:
        # golongan2
        if cpnscek.nama_id == 19 or cpnscek.nama_id == 20 or cpnscek.nama_id == 21:
            cpnscek.mk_tahun = 3
            cpnscek.mk_bulan = 0
            cpnscek.save()
            # mkpns
            jarak = relativedelta(pnscek.tanggal, cpnscek.tanggal)
            pnscek.mk_tahun = jarak.years + cpnscek.mk_tahun
            pnscek.mk_bulan = jarak.months + cpnscek.mk_bulan
            pnscek.save()
            if pangkatgolongan:
                for i in golongandasarfilter:
                    if pangkatgolongan.nama_id < 22:
                        jaraka1 = relativedelta(pangkatgolongan.tanggal, pnscek.tanggal)
                        pangkatgolongan.mk_tahun = jaraka1.years + cpnscek.mk_tahun
                        pangkatgolongan.mk_bulan = jaraka1.months + cpnscek.mk_bulan
                        pangkatgolongan.save()
                    elif pangkatgolongan.nama_id >= 22:
                        # print(pangkatgolongan.nama_id, pangkatgolongan.tanggal)
                        jarak2 = relativedelta(pangkatgolongan.tanggal, pnscek.tanggal)
                        pangkatgolongan.mk_tahun = (jarak2.years + pnscek.mk_tahun)-5
                        pangkatgolongan.mk_bulan = jarak2.months + pnscek.mk_bulan
                        pangkatgolongan.save()
                        if pangkatgolongan.mk_tahun < 0:
                            pangkatgolongan.mk_tahun = 0
                            pangkatgolongan.mk_bulan = 0
                            pangkatgolongan.save()
                        elif pangkatgolongan.mk_bulan >= 12:
                            bulanlebih = pangkatgolongan.mk_bulan - 12
                            pangkatgolongan.mk_bulan = bulanlebih
                            pangkatgolongan.mk_tahun = pangkatgolongan.mk_tahun + 1
                            pangkatgolongan.save()
        elif cpnscek.nama_id == 18:
            cpnscek.mk_tahun = 0
            cpnscek.mk_bulan = 0
            cpnscek.save()

            # mkpns
            jarak = relativedelta(pnscek.tanggal, cpnscek.tanggal)
            pnscek.mk_tahun = jarak.years + cpnscek.mk_tahun
            pnscek.mk_bulan = jarak.months + cpnscek.mk_bulan
            pnscek.save()

            # mkall
            if pangkatgolongan:
                for i in golongandasarfilter:
                    if pangkatgolongan.nama_id < 22:
                        jaraka1 = relativedelta(pangkatgolongan.tanggal, cpnscek.tanggal)
                        pangkatgolongan.mk_tahun = jaraka1.years + cpnscek.mk_tahun
                        pangkatgolongan.mk_bulan = jaraka1.months + cpnscek.mk_bulan
                        pangkatgolongan.save()

                    elif pangkatgolongan.nama_id >= 22:
                        jarak2 = relativedelta(pangkatgolongan.tanggal, pnscek.tanggal)
                        pangkatgolongan.mk_tahun = (jarak2.years + pnscek.mk_tahun)-5
                        pangkatgolongan.mk_bulan = jarak2.months + pnscek.mk_bulan
                        pangkatgolongan.save()
                        if pangkatgolongan.mk_tahun < 0:
                            pangkatgolongan.mk_tahun = 0
                            pangkatgolongan.mk_bulan = 0
                            pangkatgolongan.save()
                        elif pangkatgolongan.mk_bulan >= 12:
                            bulanlebih = pangkatgolongan.mk_bulan - 12
                            pangkatgolongan.mk_bulan = bulanlebih
                            pangkatgolongan.mk_tahun = pangkatgolongan.mk_tahun + 1
                            pangkatgolongan.save()
        else:
            cpnscek.mk_tahun = 0
            cpnscek.mk_bulan = 0
            cpnscek.save()

            # mkpsn
            jarak = relativedelta(pnscek.tanggal, cpnscek.tanggal)
            pnscek.mk_tahun = jarak.years + cpnscek.mk_tahun
            pnscek.mk_bulan = jarak.months + cpnscek.mk_bulan
            pnscek.save()

            # mkall
            if pangkatgolongan:
                jarak = relativedelta(pangkatgolongan.tanggal, cpnscek.tanggal)
                pangkatgolongan.mk_tahun = jarak.years + cpnscek.mk_tahun
                pangkatgolongan.mk_bulan = jarak.months + cpnscek.mk_bulan
                pangkatgolongan.save()
                if pangkatgolongan.mk_bulan >= 12:
                    bulanlebih = pangkatgolongan.mk_bulan - 12
                    pangkatgolongan.mk_bulan = bulanlebih
                    pangkatgolongan.mk_tahun = pangkatgolongan.mk_tahun + 1
                    pangkatgolongan.save()

    return redirect('pegawai:riwayatpangkat', data.nip)


def ProsesBerkalaView(request, id):
    request.session['username']
    tmtkgb = request.session['tmtkgb']
    pegawai = get_object_or_404(PegawaiModel, id=id)
    gol = get_object_or_404(GolonganModel, id=pegawai.golongan_id)
    datagol = GolonganHistoryModel.objects.filter(pengguna=pegawai.id).order_by('-tanggal').first()
    gaji = get_object_or_404(GajiModel, masa_kerja=datagol.mk_tahun, golongan_id=gol.id)
    tmt_kgb = datetime.datetime.strptime(tmtkgb, '%Y-%m-%d').date()
    jarak = relativedelta(tmt_kgb, datagol.tanggal)
    mkbarutahun = jarak.years + datagol.mk_tahun
    mkbarubulan = jarak.months + datagol.mk_bulan
    usulan =  NominatifxModels.objects.filter(pegawai_id = pegawai.id)
    proses = ProsesBerkalaModel.objects.filter(pegawai_id = pegawai.id)
    berkas = request.POST.getlist('berkascheck')
    if request.method == 'POST':
        if berkas == ['skpangkat','skkgb','skp']:
            print(pegawai.opd_id, pegawai.golongan_id, gaji.id, pegawai.jabatan,datagol.mk_tahun, tmt_kgb, mkbarutahun, jarak.years, mkbarubulan, jarak.months)
            if mkbarubulan >= 12:
                mkbarubulan = mkbarubulan - 12
                mkbarutahun = mkbarutahun + 1
                if mkbarutahun % 2 == 0 and mkbarubulan == 0 and usulan.exists() == False and proses.exists() == False:
                    NominatifxModels.objects.create(
                        golongan_id=pegawai.golongan_id, 
                        gaji_id=gaji.id,
                        jabatan=pegawai.jabatan, 
                        mk_tahun=datagol.mk_tahun, 
                        mk_bulan=datagol.mk_bulan,
                        mkb_tahun=mkbarutahun, 
                        mkb_bulan=mkbarubulan,
                        pegawai_id=pegawai.id, 
                        opd_id=pegawai.opd_id, 
                        tmt_kgb=tmt_kgb)
                elif usulan.exists() == True:
                    return HttpResponse('Data sudah diusulkan..!!!')
                elif proses.exists() == True:
                    return HttpResponse('Data sedang diproses..!!!')
                else:
                    return HttpResponse("Hitung Otomatis terdapat kesalahan, silahkan hitung dengan Nominatif manual")
        else:
            return HttpResponse("Berkas tidak Lengkap")  
    return redirect('pegawai:nominatif')


def HapusNominatif(request, id):
    hapus = get_object_or_404(NominatifxModels, id = id)
    hapus.delete()
    return redirect('pegawai:nominatiflist')



class NominatifManual(ListView):
    model = PegawaiModel
    ordering = ['tmt_cpns']
    template_name = 'pegawai/nominatifmanuallist.html'
    paginate_by = 25

    def get_queryset(self):
        self.request.session['username']
        opdakses = self.request.session['opd_akses']
        self.queryset = self.model.objects.filter(opd_id=opdakses)
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, PegawaiModel):
                queryset = self.queryset.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset


def CariManualNominatif(request):
    userdata = request.session['username']
    opdakses = request.session['opd_akses']
    queryset = PegawaiModel.objects.all()
    user = User.objects.get(username= userdata)
    akun = get_object_or_404(AkunModel, akun_id= user.id )
    opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
    print(list(opdnya))
    cari = request.GET.get('search', '')
    if cari is not None and cari != '':
    #     caripegawai = PegawaiModel.objects.filter(
    #         opd_id=opdakses, nama__icontains=cari)
    # else:
    #     return redirect('pegawai:pegawai')
    # return render(request, 'pegawai/nominatifmanuallist.html', {'object_list': caripegawai})
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            caripegawai = PegawaiModel.objects.filter(nama__icontains=cari)
            return render(request, 'pegawai/nominatifmanuallist.html', {'object_list': caripegawai})
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True: 
            caripegawai = PegawaiModel.objects.filter(opd_id=akun.opd_akses_id, nama__icontains=cari)
            return render(request, 'pegawai/nominatifmanuallist.html', {'object_list': caripegawai})
        elif opdakses == 'operator':
            caripegawai = PegawaiModel.objects.filter(opd_id__in=list(opdnya), nama__icontains=cari)
            return render(request, 'pegawai/nominatifmanuallist.html', {'object_list': caripegawai})
        
        else:
            return redirect('pegawai:pegawai')
    return render(request, 'pegawai/nominatifmanuallist.html', {'object_list': caripegawai})



def ProsesManualNominatif(request, id):
    template_name = 'pegawai/prosesnominatifmanual.html'
    pegawai = get_object_or_404(PegawaiModel, id=id)
    gol = get_object_or_404(GolonganModel, id=pegawai.golongan_id)
    golajuan = GolonganHistoryModel.objects.filter(pengguna=pegawai.id).order_by('-tanggal').first()
    gaji = get_object_or_404(GajiModel, masa_kerja=golajuan.mk_tahun, golongan_id=gol.id)
    
    context = {
        'pegawai': pegawai,
        'golongan': gol,
        'golajuan': golajuan
    }
    if request.method == 'POST':
        tmtkgb = request.POST.get('tmtkgb')
        tmtkgb = datetime.datetime.strptime(tmtkgb, '%Y-%m-%d').date()
        jarak = relativedelta(tmtkgb, golajuan.tanggal)
        mkbarutahun = jarak.years + golajuan.mk_tahun
        mkbarubulan = jarak.months + golajuan.mk_bulan
        if mkbarubulan >= 12:
            mkbarubulan = mkbarubulan - 12
            mkbarutahun = mkbarutahun + 1
            print(pegawai.opd_id, pegawai.golongan_id, gaji.id, pegawai.jabatan, tmtkgb, golajuan.mk_tahun, golajuan.mk_bulan, mkbarutahun, mkbarubulan, jarak.years, jarak.months)
            if mkbarutahun % 2 != 0 or mkbarubulan > 0 :
                return HttpResponse("Salah Input TMT KGB")
            else:
                NominatifxModels.objects.get_or_create(
                    golongan_id=pegawai.golongan_id,
                    gaji_id=gaji.id,
                    jabatan=pegawai.jabatan,
                    mk_tahun=golajuan.mk_tahun,
                    mk_bulan=golajuan.mk_bulan,
                    mkb_tahun=mkbarutahun,
                    mkb_bulan=mkbarubulan,
                    pegawai_id=pegawai.id,
                    opd_id=pegawai.opd_id,
                    tmt_kgb=tmtkgb
                    )
        else:
            NominatifxModels.objects.get_or_create(
                    golongan_id=pegawai.golongan_id,
                    gaji_id=gaji.id,
                    jabatan=pegawai.jabatan,
                    mk_tahun=golajuan.mk_tahun,
                    mk_bulan=golajuan.mk_bulan,
                    mkb_tahun=mkbarutahun,
                    mkb_bulan=mkbarubulan,
                    pegawai_id=pegawai.id,
                    opd_id=pegawai.opd_id,
                    tmt_kgb=tmtkgb
                    )
    return render(request, template_name, context)


class OpdListView(ListView):
    template_name = 'admin/uploadperopd.html'
    model = OpdModel

    def get_queryset(self, *args, **kwargs):
        qs = super(OpdListView, self).get_queryset(*args, **kwargs)
        qs = qs.order_by("nama")
        return qs


def LoadPegawaiView(request, id=None):
    opd = OpdModel.objects.get(id=id)
    try:
        openjson = urlopen(urlcompany + str(opd.id))
    except SocketError as e:
        if e.errno != errno.ECONNRESET:
            raise # Not error we are looking for
        pass # Handle error here.  
    data = json.load(openjson)
    for pegawai in data:
        try:
            x =str(pegawai['nip'])
            tahun = int(x[0:4])
            bulan = int(x[4:6])
            tanggal = int(x[6:8])
            lahir = datetime.date(tahun, bulan, tanggal)
            cpnstahun = datetime.date(int(x[8:12]), int(x[12:14]), 1)
            print(cpnstahun)
            inputdata = PegawaiModel.objects.update_or_create(
                id=pegawai['id'],
                nama=pegawai['name'],
                nip=pegawai['nip'],
                pengguna=pegawai['user_id'],
                golongan_id=pegawai['golongan_id'],
                opd_id=pegawai['company_id'],
                jenis_kelamin=pegawai['jenis_kelamin'],
                tempat_lahir = pegawai['tempat_lahir'],
                jabatan_data = pegawai['jabatan_data'],
                jenis_jabatan = pegawai['jenis_jabatan'],
                pddk_terakhir = pegawai['Level_Pendidikan'],
                tmt_pns = pegawai['tmt_pns'],
                tmt_cpns = cpnstahun,
                tgllahir = lahir
            )
        except :
            pass
        cekdata = PegawaiModel.objects.exclude(
            nip__isnull=False).exclude(nip__exact="").delete()
    return redirect('pegawai:pegawai')


def UpdateDataPegawai(request, id):
    pegawai = get_object_or_404(PegawaiModel, id=id)
    gol = get_list_or_404(GolonganHistoryModel, pengguna= pegawai.id)
    tahun = int(pegawai.nip[0:4])
    bulan = int(pegawai.nip[4:6])
    tanggal = int(pegawai.nip[6:8])
    print(tanggal, bulan, tahun)
    # tgllahir = datetime.date(bulan, tanggal, tahun)
    try :
        openjson = urlopen(urlpegawai + str(pegawai.nip))
        pktjson = urlopen(urlpangkat+ str(pegawai.id))
        data = json.load(openjson)
        pktdata = json.load(pktjson)
        jmlpkt = (len(pktdata))
        for i in pktdata:
            print(i['id'])
        for x in data:
            pegawai.golongan_id=x['golongan_id']
            pegawai.opd_id=x['company_id']
            pegawai.save()
    except SocketError as e:
        if e.errno != errno.ECONNRESET:
            raise # Not error we are looking for
        pass # Handle error here.
    return redirect('pegawai:detail', pegawai.id)


# class SelesaiList(ListView):
#     model = NominatifSelesaiModels
#     ordering = ['tmt_kgb']
#     template_name = "selesailist.html"

#     def get_queryset(self):
#         self.request.session['username']
#         opdakses = self.request.session['opd_akses']
#         queryset = self.model.objects.filter(opd=opdakses)
#         for data in queryset:
#             print(data.pegawai)
#         return queryset

class SelesaiList(ListView):
    model = NominatifSelesaiModels
    ordering = ['tmt_kgb']
    template_name = 'pegawai/nominatifselesaimodels_list.html'
    paginate_by = 25

    def get_queryset(self,):
        userdata = self.request.session['username']
        user = User.objects.get(username= userdata)
        opdakses = self.request.session['opd_akses']
        akun = get_object_or_404(AkunModel, akun_id= user.id )
        opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
        print(userdata, user.is_active, user.is_staff, user.is_superuser)
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            queryset = NominatifSelesaiModels.objects.all()
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
            queryset = NominatifSelesaiModels.objects.filter(opd_id =akun.opd_akses_id)
        elif opdakses == 'operator':
            queryset = NominatifSelesaiModels.objects.filter(opd_id__in=list(opdnya))
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset



def CetakSelesai(request, id):
    request.session['username']
    opdakses = request.session['opd_akses']
    template_path = 'pegawai/cetakpdf.html'
    pegawai = get_object_or_404(PegawaiModel, id=id)
    pangkat = GolonganHistoryModel.objects.filter(nama_id=pegawai.golongan, pengguna=pegawai.id).first()
    # pangkat = get_object_or_404(GolonganHistoryModel, nama_id=pegawai.golongan, pengguna=pegawai.id)
    simbol = get_object_or_404(GolonganModel, id=pegawai.golongan_id)
    nominatif = get_object_or_404(ProsesBerkalaModel, pegawai_id=pegawai.id)
    gajibaru = get_object_or_404(GajiModel, golongan_id=pegawai.golongan, masa_kerja=nominatif.mkb_tahun)
    gajilama = get_object_or_404(GajiModel, golongan_id=pegawai.golongan, masa_kerja=nominatif.mk_tahun)
    opd = get_object_or_404(OpdModel, id=pegawai.opd_id)
    kgbnext = nominatif.tmt_kgb+relativedelta(years=+2)
    inputselesai = NominatifSelesaiModels.objects.create(
        golongan_id=nominatif.golongan_id,
        gaji_id=nominatif.gaji_id,
        jabatan=nominatif.jabatan,
        mk_tahun=nominatif.mk_tahun,
        mk_bulan=nominatif.mk_bulan,
        mkb_tahun=nominatif.mkb_tahun,
        mkb_bulan=nominatif.mkb_bulan,
        pegawai_id=nominatif.pegawai_id,
        opd_id=nominatif.opd_id,
        tmt_kgb=nominatif.tmt_kgb
        )
    nominatif.delete()
    return redirect('pegawai:selesai')

def ProsesDetail(request, id):
    request.session['username']
    opdakses = request.session['opd_akses']
    data = get_object_or_404(PegawaiModel, id=id)
    gol = get_object_or_404(GolonganModel, id =data.golongan_id)
    pangkat = GolonganHistoryModel.objects.filter(pengguna=data.id, nama=data.golongan).first()
    # pangkat = get_object_or_404(GolonganHistoryModel, pengguna=data.id, nama=data.golongan)
    nominatif = get_object_or_404(ProsesBerkalaModel, pegawai_id=data.id)
    gaji = get_object_or_404(GajiModel, id=nominatif.gaji_id)
    return render(request, "pegawai/detailnominatif.html", {'pangkat': pangkat,  'data': data, 'nom': nominatif, 'gaji': gaji})

def ProsesDetailPost(request, id):
    data = get_object_or_404(PegawaiModel, id = id)
    nominatif = get_object_or_404(NominatifxModels, pegawai_id = data.id)
    print(data.id)
    inputproses = ProsesBerkalaModel.objects.get_or_create(
        golongan_id=nominatif.golongan_id,
        gaji_id=nominatif.gaji_id,
        jabatan=nominatif.jabatan,
        mk_tahun=nominatif.mk_tahun,
        mk_bulan=nominatif.mk_bulan,
        mkb_tahun=nominatif.mkb_tahun,
        mkb_bulan=nominatif.mkb_bulan,
        pegawai_id=nominatif.pegawai_id,
        opd_id=nominatif.opd_id,
        tmt_kgb=nominatif.tmt_kgb
        )
    nominatif.delete()
    return redirect('pegawai:nominatiflist')
    
class NominatifManuallist(ListView):
    model = PegawaiModel
    ordering = ['tmt_cpns']
    template_name = 'pegawai/nominatifmanuallist.html'
    paginate_by = 25

    def get_queryset(self,):
        userdata = self.request.session['username']
        user = User.objects.get(username= userdata)
        opdakses = self.request.session['opd_akses']
        akun = get_object_or_404(AkunModel, akun_id= user.id )
        opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
        print(userdata, user.is_active, user.is_staff, user.is_superuser)
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            queryset = PegawaiModel.objects.all()
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
            queryset = PegawaiModel.objects.filter(opd_id =akun.opd_akses_id)
        elif opdakses == 'operator':
            queryset = PegawaiModel.objects.filter(opd_id__in=list(opdnya))
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }and user.is_staff
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

class ProsesBerkalaList(ListView):
    model = ProsesBerkalaModel
    ordering = ['tmt_kgb']
    template_name = "prosesberkalamodel_list.html"

    def get_queryset(self,):
        userdata = self.request.session['username']
        user = User.objects.get(username= userdata)
        opdakses = self.request.session['opd_akses']
        akun = get_object_or_404(AkunModel, akun_id= user.id )
        opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
        print(userdata, user.is_active, user.is_staff, user.is_superuser)
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            queryset = ProsesBerkalaModel.objects.all()
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
            queryset = ProsesBerkalaModel.objects.filter(opd_id =akun.opd_akses_id)
        elif opdakses == 'operator':
            queryset = ProsesBerkalaModel.objects.filter(opd_id__in=list(opdnya))
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset


def SelesaiDetail(request, id):
    request.session['username']
    opdakses = request.session['opd_akses']
    data = get_object_or_404(PegawaiModel, id=id)
    gol = get_object_or_404(GolonganModel, id =data.golongan_id)
    pangkat = GolonganHistoryModel.objects.filter(pengguna=data.id, nama=data.golongan).first()
    print(pangkat, "SELESAI DETAIL")
    # pangkat = get_object_or_404(GolonganHistoryModel, pengguna=data.id, nama=data.golongan)
    nominatif = get_object_or_404(ProsesBerkalaModel, pegawai_id=data.id)
    gaji = get_object_or_404(GajiModel, id=nominatif.gaji_id)
    return render(request, "pegawai/selesainominatif.html", {'pangkat': pangkat,  'data': data, 'nom': nominatif, 'gaji': gaji})

def CetakDetail(request, id):
    request.session['username']
    opdakses = request.session['opd_akses']
    data = get_object_or_404(PegawaiModel, id=id)
    gol = get_object_or_404(GolonganModel, id =data.golongan_id)
    pangkat = GolonganHistoryModel.objects.filter(pengguna=data.id, nama=data.golongan).first()
    print(pangkat)
    # pangkat = get_object_or_404(GolonganHistoryModel, pengguna=data.id, nama=data.golongan)
    nominatif = get_object_or_404(NominatifSelesaiModels, pegawai_id=data.id)
    gaji = get_object_or_404(GajiModel, id=nominatif.gaji_id)
    return render(request, "pegawai/selesaidetail.html", {'pangkat': pangkat,  'data': data, 'nom': nominatif, 'gaji': gaji, 'opdakses':opdakses})

def CetakBerkala(request, id):
    opdakses = request.session['opd_akses']
    template_path = 'pegawai/cetakpdf.html'
    pegawai = get_object_or_404(PegawaiModel, id=id)
    pangkat = GolonganHistoryModel.objects.filter( nama_id=pegawai.golongan, pengguna=pegawai.id).first()
    simbol = get_object_or_404(GolonganModel, id=pegawai.golongan_id)
    nominatif = get_object_or_404(NominatifSelesaiModels, pegawai_id=pegawai.id)
    gajilama = get_object_or_404(GajiModel, golongan_id=pegawai.golongan, masa_kerja=nominatif.mk_tahun)
    opd = get_object_or_404(OpdModel, id=pegawai.opd_id)
    bkd = get_object_or_404(OpdModel, id = 937 )
    kepalbkd = get_object_or_404(PegawaiModel, id = bkd.kepala_opd_id)
    kgbnext = nominatif.tmt_kgb+relativedelta(years=+2)
    pensiun = get_object_or_404(JabatanModel, id = pegawai.jabatan_id)
    umur = relativedelta(kgbnext ,pegawai.tgllahir)
    print(umur.years, umur.months, umur.days, pensiun.bup, bkd.kepala_opd, opdakses)
    bup = relativedelta(months=0, years=pensiun.bup, days=0)
    pensiun = umur.years > bup.years
    try:
        gajibaru= GajiModel.objects.get(golongan_id=pegawai.golongan, masa_kerja=nominatif.mkb_tahun)
        # gajibaru = get_object_or_404(GajiModel, golongan_id=pegawai.golongan, masa_kerja=nominatif.mkb_tahun)
    except GajiModel.DoesNotExist:
        kgbnext= "MAKSIMAL"

    # pensiun = get_object_or_404(JabatanModel, id = pegawai.jabatan)
    # kepelaopd = get_object_or_404(PegawaiModel, id=opd.kepala_opd)
    rom = roman.toRoman((nominatif.tanggal).month)
    rim = (nominatif.tanggal).year
    tanggal = datetime.datetime.strftime(nominatif.tanggal, "%d %B %Y")
    cekplt = bkd.plt
    print(tanggal, cekplt, bkd.kepala_opd_id)
    context = {
        'nominatif': nominatif, 
        'data': pegawai, 
        'pangkat': pangkat,
        'gajibaru': gajibaru, 
        'gajilama': gajilama, 
        'kgbnext': kgbnext, 
        'simbol': simbol,
        'pensiun':pensiun,
        'rom':rom,
        'rim':rim,
        'tanggal':tanggal,
        'kepalabkd':kepalbkd,
        'cekplt':cekplt,
        'opdakses':opdakses
        }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def PangkatDetail(request, id):
    gol= get_object_or_404(GolonganHistoryModel, id=id)
    pegawai = get_object_or_404(PegawaiModel, id= gol.pengguna)
    form = GolonganHistoryForm(request.POST or None, instance= gol)
    context= {'form': form}
    if form.is_valid():
        # obj= form.save(commit= False)
        # obj.save()
        obj = form.save(commit=True)
        obj.save()
        messages.success(request, "Berhasil Update Data Pangkat")
        context= {'form': form}
        return render(request, 'pegawai/detailpangkat.html', context)
    else:
        context= {'form': form,'error': 'Data Pangkat Belum Diupdate'}
    return render(request,'pegawai/detailpangkat.html' , context)


class ProsesBerkalaPegawaiAll(ListView):
    model = ProsesBerkalaModel
    ordering = ['tmt_kgb']
    template_name = "prosesberkalamodelall_list.html"

    def get_queryset(self,):
        userdata = self.request.session['username']
        user = User.objects.get(username= userdata)
        opdakses = self.request.session['opd_akses']
        akun = get_object_or_404(AkunModel, akun_id= user.id )
        opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
        print(userdata, user.is_active, user.is_staff, user.is_superuser)
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            queryset = ProsesBerkalaModel.objects.all()
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
            queryset = ProsesBerkalaModel.objects.filter(opd_id =opdakses)
        elif opdakses == 'operator':
            queryset = ProsesBerkalaModel.objects.filter(opd_id__in=list(opdnya))
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

class NominatifTunda(ListView):
    model = NominatifTundaModel
    ordering = ['tmt_kgb']
    template_name = 'pegawai/nominatiflist.html'
    paginate_by = 25

    def get_queryset(self,):
        userdata = self.request.session['username']
        user = User.objects.get(username= userdata)
        opdakses = self.request.session['opd_akses']
        akun = get_object_or_404(AkunModel, akun_id= user.id )
        opdnya = OpdModel.objects.filter(operator_id=akun.akun_id).values_list('id', flat=True)
        if opdakses == 'admin':
        # if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
            queryset = NominatifTundaModel.objects.all()
        elif opdakses == 'operatoropd':
        # elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
            queryset = NominatifTundaModel.objects.filter(opd_id =akun.opd_akses_id)
        elif opdakses == 'operator':
            queryset = NominatifTundaModel.objects.filter(opd_id__in =list(opdnya))
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

def CetakDaftarNominatif(request):
    userdata = request.session['username']
    user = User.objects.get(username= userdata)
    opdakses = request.session['opd_akses']
    template_path = 'pegawai/cetaknominatif.html'
    # pegawai = get_object_or_404(PegawaiModel, id=id)
    akun = get_object_or_404(AkunModel, akun_id= user.id )
    nominatif = NominatifxModels.objects.filter(opd_id = akun.opd_akses_id)
    for data in nominatif:
        datapegawai = get_object_or_404(PegawaiModel, id = data.pegawai_id)
        opd = get_object_or_404(OpdModel, id = datapegawai.opd_id)
        kepalaopd = get_object_or_404(PegawaiModel, id = opd.kepala_opd_id)
        cekplt = opd.plt
        print(cekplt)
        
        context = {
            'nominatiflist': nominatif,
            'datapegawai':datapegawai,
            'kepalaopd':kepalaopd,
            'cekplt':cekplt
            }
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="nominatif.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def TundaView(request, id):
    data = get_object_or_404(ProsesBerkalaModel, id=id)
    pegawai = get_object_or_404(PegawaiModel, id = data.pegawai_id)
    gaji = get_object_or_404(GajiModel, golongan_id = data.golongan_id, masa_kerja=data.mk_tahun)
    golongan = get_object_or_404(GolonganModel, id=data.golongan_id)
    form= TundaForm(request.POST or None, instance = data)
    if request.method == 'POST':
        context = {'form':form}
        if form.is_valid():
            keterangan = request.POST.get('keterangan')
            NominatifTundaModel.objects.get_or_create(
                golongan = data.golongan,
                gaji = data.gaji,
                jabatan = data.jabatan,
                mk_tahun = data.mk_tahun,
                mk_bulan = data.mk_bulan,
                mkb_tahun = data.mkb_tahun,
                mkb_bulan = data.mkb_bulan,
                pegawai = data.pegawai,
                opd = data.opd,
                tanggal = data.tanggal,
                tmt_kgb = data.tmt_kgb,
                keterangan = keterangan
            )
            data.delete()
            return redirect('pegawai:berkalalist')
        else:
            pass
        return render(request, 'pegawai/tundadetail.html',context)
    return render(request, 'pegawai/tundadetail.html',{'form':form})
    
    
def TundaDelete(request, id):
    template_name = 'pegawai/nominatiftundamodel_list.html'
    userdata = self.request.session['username']
    user = User.objects.get(username= userdata)
    opdakses = self.request.session['opd_akses']
    print(userdata, user.is_active, user.is_staff, user.is_superuser)
    if user.is_superuser == True and user.is_staff == True and user.is_active == True and AkunModel.objects.get(opd_akses_id = 1):
        queryset = NominatifTundaModel.objects.all()
    elif user.is_superuser == False and user.is_staff == True and user.is_active == True:
        queryset = NominatifTundaModel.objects.filter(opd_id =opdakses)
    tundadata = get_object_or_404(NominatifTundaModel, id =id)
    tundadata.delete()
    return render(request, template_name, {'object_list':queryset})



# delete view for details
def TundaDeleteView(request, id):
	context ={}
	obj = get_object_or_404(NominatifTundaModel, id = id)
	if request.method =="POST":
		# delete object
		obj.delete()
		# after deleting redirect to
		# home page
		return redirect("pegawai:tunda")
	return render(request, "pegawai/delete_view.html", {'context':context, 'obj':obj})


def EditJabatanView(request, id):
    template_name = 'pegawai/editjabatan.html'
    obj = get_object_or_404(PegawaiModel, id = id)
    jabatan = JabatanModel.objects.all().order_by('nama')
    context = {
        'obj':obj,
        'jabatan':jabatan
        }
    if request.method =="POST":
        jenis = request.POST.get('jenis')
        print(jenis)
        obj.jabatan_id = jenis
        obj.save()
        return redirect('pegawai:detail', obj.id)
    return render(request, template_name, context)


def AddPegawaiView (request):
    pegawai = PegawaiModel.objects.all()
    if request.method == 'POST':
        nip = request.POST.get('nip')
        try:
            openjson = urlopen(urlpegawai+ nip)
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise # Not error we are looking for
            pass # Handle error here. 
        data = json.load(openjson)
        x = data[0]
        print(x['nip'],x['company_id'],x['name'])
        addpegawai = pegawai.filter( id =x['id'])
        if addpegawai.exists():
            return HttpResponse("data sudah ada")
        else:
            y =str(x['nip'])
            tahun = int(y[0:4])
            bulan = int(y[4:6])
            tanggal = int(y[6:8])
            lahir = datetime.date(tahun, bulan, tanggal)
            cpnstahun = datetime.date(int(y[8:12]), int(y[12:14]), 1)
            print(cpnstahun)
            inputdata = PegawaiModel.objects.update_or_create(
                id=x['id'],
                nama=x['name'],
                nip=x['nip'],
                pengguna=x['user_id'],
                golongan_id=x['golongan_id'],
                opd_id=x['company_id'],
                jenis_kelamin=x['jenis_kelamin'],
                tempat_lahir = x['tempat_lahir'],
                jabatan_data = x['jabatan_data'],
                jenis_jabatan = x['jenis_jabatan'],
                pddk_terakhir = x['Level_Pendidikan'],
                tmt_pns = x['tmt_pns'],
                tmt_cpns = cpnstahun,
                tgllahir = lahir
            )
            return HttpResponse("Berhasil Add Pegawai")
    return render(request,'admin/addpegawai.html')

class DeletePangkatView(DeleteView):
    # specify the model you want to use
    model = GolonganHistoryModel
     
    # can specify success url
    # url to redirect after successfully
    # deleting object
    success_url = reverse_lazy ("pegawai:pegawai")
     
    template_name = "pegawai/confirmdelete.html"
    
