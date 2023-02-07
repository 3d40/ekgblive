from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

# Create your models here.
class PegawaiModel(models.Model):
    KELAMIN_CHOICE = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan')
    ]
    nama = models.CharField(max_length=100)
    jabatan = models.ForeignKey('JabatanModel', models.DO_NOTHING, default='7', null=True)
    nip = models.CharField(max_length=100, null=True)
    opd = models.ForeignKey('OpdModel', models.DO_NOTHING, blank=True, null=True)
    golongan = models.ForeignKey('GolonganModel', models.DO_NOTHING, null=True, blank=True)
    pengguna = models.IntegerField(blank=True, null=True)
    alamat  = models.CharField(max_length=255)
    telpon  = models.CharField(max_length=30)
    gaji_skrg = models.IntegerField(blank=True, null=True, default=0)
    tmt_cpns = models.DateField(default=datetime.datetime.now, null=True, blank=True)
    fhoto = models.ImageField(upload_to ='upload/fhoto/')
    nominasi = models.BooleanField(default=False)
    jenis_kelamin = models.CharField(max_length=30, choices=KELAMIN_CHOICE, blank=True, null=True)
    tempat_lahir = models.CharField(max_length=100, blank=True, null=True)
    jabatan_data = models.CharField(max_length=100, blank=True, null=True)
    jenis_jabatan =  models.CharField(max_length=100, blank=True, null=True)
    pddk_terakhir = models.CharField(max_length=100, blank=True, null=True)
    tmt_pns = models.DateField(default=datetime.datetime.now, null=True, blank=True)
    tgllahir = models.DateField(null=True, blank=True, default='1990-01-01')

    def __str__(self):
        return self.nama


class GolonganModel(models.Model):
    nama = models.CharField(max_length=50)
    nilai = models.IntegerField()
    simbol =models.CharField(max_length=10, null=True)
    grade =models.IntegerField(default=0,blank=True, null=True)

    class Meta:
        managed=True,
    
    def __str__(self):
        return self.nama

class GolonganHistoryModel(models.Model):
    pengguna = models.IntegerField(null=True, blank=True)
    nip = models.CharField(max_length=50, null=True, blank=True, verbose_name= 'NIP')
    nama = models.ForeignKey('GolonganModel' ,models.DO_NOTHING, null=True,blank=True,default=24)
    nomor_sk = models.CharField(max_length=150, null=True,blank=True, default="S-10225/BKD-2.2/")
    jenis = models.CharField(max_length=50, null=True, blank=True)
    tanggal = models.DateField(default=2021-3-20, blank=True, null=True)
    gambar = models.FileField(upload_to='berkas/', blank=True, null=True)
    mk_tahun = models.IntegerField(null=True, default=0)
    mk_bulan = models.IntegerField(null=True, default=0)
    dasarnominatif = models.BooleanField(null=True, default=False)
    tglpenetapan = models.DateField(null=True, blank=True)
    pejabat = models.CharField(max_length=50, null=True, blank=True, default="GUBERNUR JAMBI")
    
    class Meta:
        managed=True,
    
    def __str__(self):
        return self.nip
        

class OpdModel(models.Model):
    nama = models.CharField(max_length=255)
    kepala_opd = models.ForeignKey('PegawaiModel', models.DO_NOTHING, null=True, blank=True, default=88761)
    alamat = models.CharField(max_length=255, null=True, blank=True)
    telpon = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    operator = models.ForeignKey('AkunModel', models.DO_NOTHING, null=True, blank=True, default=1)
    plt =models.BooleanField(default=False)
    
    def __str__(self):
        return self.nama

class JabatanModel(models.Model):
    jenis = models.CharField(max_length=20, blank=True, null=True, default='jfu')
    nama = models.CharField(max_length=150, default="")
    bup = models.IntegerField()
    jenjang = models.CharField(max_length=15)

    def __str__(self):
        return self.nama

class GajiModel(models.Model):
    masa_kerja = models.IntegerField()
    golongan = models.ForeignKey('GolonganModel', models.DO_NOTHING, blank=True, null=True)
    tbgaji_currency = models.CharField(blank=True, null=True, max_length=255)
    terbilang = models.CharField(blank=True, null=True, max_length=255)

    def __str__(self):
        return self.tbgaji_currency

class BerkalaHistoryModel(models.Model):
    username    = models.CharField(max_length=255, blank=True, null=True)
    kgb_nomor = models.CharField(max_length=255, blank=True, null=True)
    kgb_tanggal = models.DateTimeField(auto_now=True, blank=True, null=True)
    tmt         = models.DateField(blank=True, null=True)
    tmt_baru    = models.DateField(blank=True, null=True)
    golongan    = models.CharField(max_length=5)
    pejabat_ttd = models.CharField(max_length=255, default='GUBERNUR JAMBI')
    mk_lama_tahun  = models.IntegerField(blank=True, null=True)
    mk_lama_bulan  = models.IntegerField(blank=True, null=True)
    kgb_image = models.FileField(blank=True, null=True, upload_to = 'media')
    mk_baru_tahun  = models.IntegerField(blank=True, null=True)
    mk_baru_bulan  = models.IntegerField(blank=True, null=True)
    nilai= models.IntegerField(null=True, blank=True)
    dokumen = models.FileField(upload_to='skberkala/', blank=True, null=True)
    
    
    def __str__(self):
        return self.username
    

class AkunModel(models.Model):
    JENIS_AKUN_CHOICES = (
        ('pegawai','Pegawai'),
        ('operatoropd', 'OperatorOpd'),
        ('operator', 'Operator'),
        ('admin', 'Administrator'),

    )
    akun = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    pegawai = models.CharField(max_length=50, blank=True, null=True)
    jenis_akun = models.CharField(max_length=20, choices=JENIS_AKUN_CHOICES)
    opd_akses = models.ForeignKey('OpdModel', models.DO_NOTHING, blank=True, null=True)

    def __unicode__(self):
        return self.akun.nama

    def __str__(self) -> str:
        return str(self.pegawai)+' | '+str(self.opd_akses)


class ProsesBerkalaModel(models.Model):
    STATUS_CHOICES = (
        ('selesai','Selesai'),
        ('tertunda', 'Tertunda'),
        ('proses', 'Proses'),
        ('nominatif', 'Nominatif'),
    )
    golongan = models.ForeignKey('GolonganModel', models.DO_NOTHING, null=True, blank=True)
    gaji = models.ForeignKey('GajiModel', models.DO_NOTHING, blank=True, null=True)
    jabatan = models.ForeignKey('JabatanModel', models.DO_NOTHING, blank=True, null=True)
    mk_tahun = models.IntegerField(blank=True, null=True)
    mk_bulan = models.IntegerField(blank=True, null=True)
    mkb_tahun = models.IntegerField(blank=True, null=True)
    mkb_bulan = models.IntegerField(blank=True, null=True)
    pegawai = models.ForeignKey('PegawaiModel', models.DO_NOTHING, blank=True, null=True)
    opd = models.ForeignKey('OpdModel', models.DO_NOTHING, blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=timezone.now, blank=True)
    tmt_kgb = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, default='nominatif')

    def __str__(self):
        return self.status

class NominatifxModels(models.Model):
    bahanchoice = (
        ('l','Lengkap'),
        ('tl', 'Tidak Lengkap'),
    )
    
    golongan = models.ForeignKey('GolonganModel', models.DO_NOTHING, null=True, blank=True)
    gaji = models.ForeignKey('GajiModel', models.DO_NOTHING, blank=True, null=True)
    jabatan = models.ForeignKey('JabatanModel', models.DO_NOTHING, blank=True, null=True)
    mk_tahun = models.IntegerField(blank=True, null=True)
    mk_bulan = models.IntegerField(blank=True, null=True)
    mkb_tahun = models.IntegerField(blank=True, null=True)
    mkb_bulan = models.IntegerField(blank=True, null=True)
    pegawai = models.ForeignKey('PegawaiModel', models.DO_NOTHING, blank=True)
    opd = models.ForeignKey('OpdModel', models.DO_NOTHING, blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=timezone.now, blank=True)
    tmt_kgb = models.DateField(blank=True, null=True)
    bahan = models.CharField(max_length=20, choices=bahanchoice, blank=True)
    
    def __str__(self):
        return self.bahan


class NominatifSelesaiModels(models.Model):    
    golongan = models.ForeignKey('GolonganModel', models.DO_NOTHING, null=True, blank=True)
    gaji = models.ForeignKey('GajiModel', models.DO_NOTHING, blank=True, null=True)
    jabatan = models.ForeignKey('JabatanModel', models.DO_NOTHING, blank=True, null=True)
    mk_tahun = models.IntegerField(blank=True, null=True)
    mk_bulan = models.IntegerField(blank=True, null=True)
    mkb_tahun = models.IntegerField(blank=True, null=True)
    mkb_bulan = models.IntegerField(blank=True, null=True)
    pegawai = models.ForeignKey('PegawaiModel', models.DO_NOTHING, blank=True)
    opd = models.ForeignKey('OpdModel', models.DO_NOTHING, blank=True, null=True)
    tanggal = models.DateTimeField(auto_now_add=timezone.now, blank=True)
    tmt_kgb = models.DateField(blank=True, null=True)
    qrcode = models.ImageField(upload_to='qrbarcode/', null=True, blank=True)
    
    def __str__(self):
        return str(self.tmt_kgb)

class NominatifTundaModel(models.Model):    
    golongan = models.ForeignKey('GolonganModel', models.DO_NOTHING, null=True, blank=True)
    gaji = models.ForeignKey('GajiModel', models.DO_NOTHING, blank=True, null=True)
    jabatan = models.ForeignKey('JabatanModel', models.DO_NOTHING, blank=True, null=True)
    mk_tahun = models.IntegerField(blank=True, null=True)
    mk_bulan = models.IntegerField(blank=True, null=True)
    mkb_tahun = models.IntegerField(blank=True, null=True)
    mkb_bulan = models.IntegerField(blank=True, null=True)
    pegawai = models.ForeignKey('PegawaiModel', models.DO_NOTHING, blank=True, verbose_name= 'Nama')
    opd = models.ForeignKey('OpdModel', models.DO_NOTHING, blank=True, null=True, verbose_name='Unit Kerja')
    tanggal = models.DateTimeField(auto_now_add=timezone.now, blank=True)
    tmt_kgb = models.DateField(blank=True, null=True, verbose_name='TMT KGB')
    keterangan = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.keterangan




