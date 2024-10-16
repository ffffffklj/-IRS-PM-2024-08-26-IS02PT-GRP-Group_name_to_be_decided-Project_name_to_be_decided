from django.urls import path

from recommendation.views import InformationView, MessageView, CityRecommendView

urlpatterns = [
    path('information', InformationView.as_view(), name='information'),
    path('message', MessageView.as_view(), name='message'),
    path('city', CityRecommendView.as_view(), name='city'),
]
