from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.redirect_to_users),
    path("", include("django.contrib.auth.urls")),
    path("signup", views.CreateUser.as_view(), name="signup"),
    path("users", views.UserList.as_view(), name="users"),
    path("users/<str:slug>", views.UserDetail.as_view(), name="user-detail"),
]

# django.contrib.auth.urls
# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']