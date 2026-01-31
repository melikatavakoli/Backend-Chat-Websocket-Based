from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.urls import path,include
from django.conf.urls.static import static
from config import settings
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    # Swagger UI
    path('api/v1/schema/', SpectacularAPIView.as_view(authentication_classes=[], permission_classes=[]), name='schema'),
    # path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/docs/',
            SpectacularSwaggerView.as_view(url_name='schema', authentication_classes=[], permission_classes=[]),
            name='swagger-ui'),
    path('api/v1/redoc/',
            SpectacularRedocView.as_view(url_name='schema', authentication_classes=[], permission_classes=[]),
            name='redoc'),
            path('api/v1/post/', include('post.urls', namespace="post"))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
