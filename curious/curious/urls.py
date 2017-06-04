from django.conf.urls import  include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Examples:
    # url(r'^$', 'curious.views.home', name='home'),
    # url(r'^blog/', include('blog.urls'))
    url(r'^', include('curiousWorkbench.urls',namespace="curiousWorkbench")),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
    url(r'^accounts/$', include('registration.backends.default.urls')),
    url(r'^accounts/$', include('registration.backends.default.urls')),
    url(r'^accounts/$', include('django.contrib.auth.urls')),
    url(r'^curiousWorkbench/', include('curiousWorkbench.urls',namespace="curiousWorkbench")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
