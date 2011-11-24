# Copyright 2011 GRNET S.A. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
# 
#   1. Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
# 
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of GRNET S.A.

from django.conf import settings
from django.conf.urls.defaults import patterns


urlpatterns = patterns('pithos.im.views',
    (r'^$', 'index'),
    (r'^login/?$', 'index'),
    
    (r'^admin/?$', 'admin'),
    
    (r'^admin/users/?$', 'users_list'),
    (r'^admin/users/(\d+)/?$', 'users_info'),
    (r'^admin/users/create$', 'users_create'),
    (r'^admin/users/(\d+)/modify/?$', 'users_modify'),
    (r'^admin/users/(\d+)/delete/?$', 'users_delete'),
    (r'^admin/users/export/?$', 'users_export'),
    
    (r'^admin/invitations/?$', 'invitations_list'),
    (r'^admin/invitations/export/?$', 'invitations_export'),
    
    (r'^profile/(\d+)/?$', 'users_profile'),
    (r'^profile/(\d+)/edit/?$', 'users_edit'),
)

urlpatterns += patterns('pithos.im.target',
    (r'^login/dummy/?$', 'dummy.login')
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                                {'document_root': settings.PROJECT_PATH + '/im/static'})
)

if 'local' in settings.IM_STANDARD_MODULES:
    urlpatterns += patterns('pithos.im.views',
        (r'^local/create/?$', 'local_create'),
        (r'^local/reclaim/?$', 'reclaim_password')
    )
    urlpatterns += patterns('pithos.im.target',
        (r'^local/?$', 'local.login'),
        (r'^local/activate/?$', 'local.activate'),
        (r'^local/reset/?$', 'local.reset_password')
    )

if 'invitation' in settings.IM_STANDARD_MODULES:
    urlpatterns += patterns('pithos.im.views',
        (r'^invite/?$', 'invite'),
    )
    urlpatterns += patterns('pithos.im.target',
        (r'^login/invitation/?$', 'invitation.login')
    )

if 'shibboleth' in settings.IM_OTHER_MODULES:
    urlpatterns += patterns('pithos.im.target',
        (r'^login/shibboleth/?$', 'shibboleth.login')
    )

if 'twitter' in settings.IM_OTHER_MODULES:
    urlpatterns += patterns('pithos.im.target',
        (r'^login/twitter/?$', 'twitter.login'),
        (r'^login/twitter/authenticated/?$', 'twitter.authenticated')
    )
