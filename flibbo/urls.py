from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('openai/', include('chat_openai.urls')),
    path('point/', include('point.urls')),
    path('category/', include('category.urls')),
    path('account/', include('accounts.urls')),
    path('network/', include('following_system.urls')),
    path('token/', include('tokens.urls')),
    path('posts/', include('posts.urls')),
    path('market/', include('marketplace.urls')),
    path('explore/', include('explore.urls')),
    path('activity/', include('activity.urls')),
    path('wallet/', include('wallet.urls')),
    path('notification/', include('notification.urls')),
    path('base/', include('flibbo_base.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
