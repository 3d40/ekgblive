from django.urls import path, include
from . import views
from .models import PegawaiModel
from django.views.generic import ListView


app_name = 'pegawai'
urlpatterns = [
    path('', views.LoginView, name='login'),
    path('logout', views.LogoutView, name='logout'),
    path('pegawai/', views.Pegawai.as_view(), name = 'pegawai'),
    path('pegawai/index', views.IndexView, name='index'),
    path('pegawai/cari', views.CariView, name = 'cari'),
    path('pegawai/detail/<int:id>', views.HitungPangkatView, name='detail'),
    path('pegawai/detail/update/<int:id>', views.UpdateDataPegawai, name='update'),  
    path('pegawai/pangkat/<int:id>', views.PangkatDetail, name='detailpangkat'),  

    
    path('pegawai/daftarnominatif', views.NominatifViews, name='nominatif'),
    path('pegawai/daftarnominatif/list', views.NominatifList.as_view(), name='nominatiflist'),
    path('pegawai/daftarnominatif/list/hapus/<int:id>', views.HapusNominatif, name='delnominatif'),
    path('pegawai/daftarnominatif/detail/<int:id>', views.NominatifDetailView, name='nominatifdetail'),
    path('pegawai/daftarnominatif/proses/<int:id>/manual', views.ProsesManualNominatif, name='prosesnominatifmanual'),

    path('pegawai/tunda/list', views.NominatifTunda.as_view(), name='tunda'),
    path('pegawai/daftarnominatif/selesai/', views.SelesaiList.as_view(), name='selesai'),
    path('pegawai/daftarnominatif/selesai/detail/<int:id>', views.SelesaiDetail, name='selesaidetail'),
    
    
    path('pegawai/daftarnominatif/manual', views.NominatifManuallist.as_view(), name='listnominatifmanual'),
    path('pegawai/daftarnominatif/manual/cari', views.CariManualNominatif, name='carinominatifmanual'),
    
    path('pegawai/riwayatpangkat/<str:nip>', views.RiwayatPangkatView, name='riwayatpangkat'),
    path('pegawai/riwayatpangkat/delete/<int:pk>', views.DeletePangkatView.as_view(), name='deletepangkat'),      
    # path('pegawai/riwayatpangkat/upload/<int:id>', views.UploadBerkasView, name='uploadberkas'),
    
    path('pegawai/prosesberkala/', views.ProsesBerkalaList.as_view(), name='berkalalist'),
    path('pegawai/prosesberkala/<int:id>', views.ProsesBerkalaView, name='prosesnominatif'), #Input Ke Nominatifxmodel 
    path('pegawai/prosesberkala/detail/<int:id>', views.ProsesDetail, name='prosesdetail'),
    path('pegawai/prosesberkala/detail/post/<int:id>', views.ProsesDetailPost, name='prosesdetailpost'), #delete di Nominatifxmodel, input ke ProsesBerkalaModel
    
    
    path('pegawai/cetak/detail/<int:id>',views.CetakDetail, name='detailcetak'),
    path('pegawai/cetak/detail/cetakberkala/<int:id>',views.CetakBerkala, name='CetakBerkala'),
    path('pegawai/cetak/<int:id>',views.CetakPdfFile, name='cetakpdf'),
    path('pegawai/cetakselesai/<int:id>',views.CetakSelesai, name='cetakselesai'),
    
    
    path('pangkat/<int:id>', views.Hitungmasakerja, name='pangkat'),
    path('pegawai/opdlist/', views.OpdListView.as_view(), name='opd'),
    path('pegawai/opdlist/<int:id>', views.LoadPegawaiView, name='loadpegawai'),
    # path('pegawai/all/', views.PegawaiAll.as_view(), name='adminpegawai'),
    # path('pegawai/all/proses/', views.ProsesBerkalaPegawaiAll.as_view(), name='adminproses'),
    # path('pegawai/all/nominatif/', views.NominatifBerkalaPegawaiAll.as_view(), name='adminnominatif'),
    
    path('pegawai/tunda/<int:id>', views.TundaView, name='tundaproses'),
    path('pegawai/tunda/delete/<int:id>', views.TundaDeleteView, name='tundadelete'),
    
    path('pegawai/jabatan/edit/<int:id>', views.EditJabatanView, name='editjabatan'),
    path('pegawai/cetakdaftarnominatif', views.CetakDaftarNominatif, name='cetaknominatif'),
    path('pegawai/addpegawai/', views.AddPegawaiView, name='addpegawai'),

    ]
    
    