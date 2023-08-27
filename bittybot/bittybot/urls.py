from django.contrib import admin
from django.urls import path
from .views import killBot, startBot, profitableCount, profitabilities, profitVsCertainty


urlpatterns = [
    path('admin/', admin.site.urls),
    path('startBot/', startBot.as_view(), name='startBot'),
    path('killBot/', killBot.as_view(), name='killBot'),
    path('profitable-count/<str:start>/', profitableCount.as_view() , name='profitable-count'),
    path('profitabilities/<str:start>/', profitabilities.as_view() , name='profitablities'),
    path('profit-vs-certainty/<str:start>/', profitVsCertainty.as_view() , name='profit-vs-certainty')
]
