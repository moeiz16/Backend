from django.urls import path
from . import views


urlpatterns = [
    path('pointwise/', views.point_wise_ndvi),
    path('average/', views.average_ndvi),
    path('polygonpointwise/', views.polygon_point_wise_ndvi),
    path('heterogeneity/', views.ndvi_heterogeneity),
]