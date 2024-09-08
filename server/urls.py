from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from app_dash import admin, views

urlpatterns = [
    re_path('login', views.login),
    re_path('signup', views.signup),
    re_path('test-token', views.test_token),

    re_path('apps/(?P<pk>[0-9]+)', views.app_detail, name='app-detail'),
    re_path('apps', views.app_list_create, name='app-list-create'),

    re_path('plans', views.plan_list, name='plan-list'),

    re_path('subscriptions/(?P<pk>[0-9]+)', views.subscription_update, name='subscription-update'),
    
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('password_reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]
