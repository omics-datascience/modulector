from django.contrib import admin
from django.urls import path
from modulector import views
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('mirna/', views.MirnaList.as_view({'get': 'list'}), name='mirna'),
    path('mirna-target-interactions/', views.MirnaTargetInteractions.as_view(),
         name='mirna_target_interactions'),
    path('mirna-aliases/', views.MirnaAliasesList.as_view(), name='mirna_aliases'),
    path('mirna-codes/', views.MirnaCodes.as_view(), name='mirna_codes'),
    path('mirna-codes-finder/', views.MirnaCodesFinder.as_view(),
         name='mirna_codes_finder'),
    path('diseases/', views.MirnaDiseaseList.as_view(), name='diseases'),
    path('drugs/', views.MirnaDrugsList.as_view(), name='drugs'),
    path('subscribe-pubmeds/', views.SubscribeUserToPubmed.as_view()),
    path('unsubscribe-pubmeds/', views.UnsubscribeUserToPubmed.as_view()),
    path('methylation/', views.MethylationDetails.as_view(), name='methylation'),
    path('methylation-sites-finder/', views.MethylationSitesFinder.as_view(),
         name='methylation_sites_finder'),
    path('methylation-sites/', views.MethylationSites.as_view(),
         name='methylation_sites'),
    path('methylation-sites-genes/', views.MethylationSitesToGenes.as_view(),
         name='methylation_sites_to_genes'),
    path('', views.index)
]
