from django.urls import path

from . import views

app_name = 'auctions'

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing", views.listing, name="listing"),
    path("item/<str:title>/", views.item, name="item"),
    path("category", views.category, name="category"),
    path("wishlist", views.wishlist, name="wishlist"),
    path("bid/<str:title>/", views.bid, name="bid")
]
