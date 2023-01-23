"""ModulectorBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from modulector import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mirna/', views.MirnaList.as_view({'get': 'list'})),
    path('process/', views.Process.as_view()),
    path('mirna-target-interactions/', views.MirnaTargetInteractions.as_view({'get': 'list'})),
    path('mirna-interactions/', views.MirnaInteractions.as_view()),
    path('mirna-aliases/', views.MirnaAliasesList.as_view()),
    path('diseases/', views.MirnaDiseaseList.as_view()),
    path('drugs/', views.MirnaDrugsList.as_view()),
    path('subscribe-pubmeds/', views.SubscribeUserToPubmed.as_view()),
    path('unsubscribe-pubmeds/', views.UnsubscribeUserToPubmed.as_view()),
    path('mirnas-finder/', views.MirnasFinder.as_view()),

    path('', views.index)
]
