from django.urls import path
from django.contrib.auth.views import TemplateView
from ads.views import *

urlpatterns = [
    path ('', AdList.as_view(), name='ad_list'),
    path('create/', AdCreate.as_view()),
    path('update/<int:pk>/', AdUpdate.as_view()),
    path('delete/<int:pk>/', AdDelete.as_view()),
    path('offers/<int:pk>/', OffersList.as_view()),
    path('offers/<int:pk>/<int:obj>/', offer_add),
    path('showcase/', UserThingList.as_view()),
    path('user_offers/', ExchangeProposalList.as_view()),
    path('offers/accept/<int:pk>', offer_accept),
    path('offers/cancel/<int:pk>', offer_cancel),
    path('detail/<int:pk>/', DetailView.as_view())
]