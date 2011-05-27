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

from django.test.client import Client
from django.test import TestCase
from django.utils import simplejson as json
from xml.dom import minidom
import types
import hashlib
import os
import mimetypes
import random
import datetime

DATE_FORMATS = ["%a %b %d %H:%M:%S %Y",
                "%A, %d-%b-%y %H:%M:%S GMT",
                "%a, %d %b %Y %H:%M:%S GMT"]

class AaiClient(Client):
    def request(self, **request):
        request['HTTP_X_AUTH_TOKEN'] = '46e427d657b20defe352804f0eb6f8a2'
        return super(AaiClient, self).request(**request)

class BaseTestCase(TestCase):
    #TODO unauthorized request
    def setUp(self):
        self.client = AaiClient()
        self.headers = {
            'account':(
                'X-Account-Container-Count',
                'X-Account-Bytes-Used',
                'Last-Modified',
                'Content-Length',
                'Date',
                'Content-Type',),
            'container':(
                'X-Container-Object-Count',
                'X-Container-Bytes-Used',
                'Content-Type',
                'Last-Modified',
                'Content-Length',
                'Date',),
            'object':(
                'ETag',
                'Content-Length',
                'Content-Type',
                'Content-Encoding',
                'Last-Modified',
                'Date',
                'X-Object-Manifest',
                'Content-Range',)}
        self.contentTypes = {'xml':'application/xml',
                             'json':'application/json',
                             '':'text/plain'}
        self.extended = {
            'container':(
                'name',
                'count',
                'bytes',
                'last_modified'),
            'object':(
                'name',
                'hash',
                'bytes',
                'content_type',
                'content_encoding',
                'last_modified',)}
        self.return_codes = (400, 401, 404, 503,)
    
    def assertFault(self, response, status_code, name):
        self.assertEqual(response.status_code, status_code)
    
    def assertBadRequest(self, response):
        self.assertFault(response, 400, 'badRequest')
    
    def assertItemNotFound(self, response):
        self.assertFault(response, 404, 'itemNotFound')

    def assertUnauthorized(self, response):
        self.assertFault(response, 401, 'unauthorized')

    def assertServiceUnavailable(self, response):
        self.assertFault(response, 503, 'serviceUnavailable')

    def assertNonEmpty(self, response):
        self.assertFault(response, 409, 'nonEmpty')

    def assert_status(self, response, codes):
        l = [elem for elem in self.return_codes]
        if type(codes) == types.ListType:
            l.extend(codes)
        else:
            l.append(codes)
        self.assertTrue(response.status_code in l)

    def get_account_meta(self, account, exp_meta={}):
        path = '/v1/%s' % account
        response = self.client.head(path)
        self.assert_status(response, 204)
        self.assert_headers(response, 'account', exp_meta)
        return response

    def list_containers(self, account, limit=10000, marker='', format=''):
        params = locals()
        params.pop('self')
        params.pop('account')
        path = '/v1/%s' % account
        response = self.client.get(path, params)
        self.assert_status(response, [200, 204])
        response.content = response.content.strip()
        if format:
            self.assert_extended(response, format, 'container', limit)
        else:
            names = get_content_splitted(response)
            self.assertTrue(len(names) <= limit)
        return response

    def update_account_meta(self, account, **metadata):
        path = '/v1/%s' % account
        response = self.client.post(path, **metadata)
        response.content = response.content.strip()
        self.assert_status(response, 202)
        return response

    def get_container_meta(self, account, container, exp_meta={}):
        params = locals()
        params.pop('self')
        params.pop('account')
        params.pop('container')
        path = '/v1/%s/%s' %(account, container)
        response = self.client.head(path, params)
        response.content = response.content.strip()
        self.assert_status(response, 204)
        if response.status_code == 204:
            self.assert_headers(response, 'container', exp_meta)
        return response

    def list_objects(self, account, container, limit=10000, marker='', prefix='', format='', path='', delimiter='', meta=''):
        params = locals()
        params.pop('self')
        params.pop('account')
        params.pop('container')
        path = '/v1/%s/%s' % (account, container)
        response = self.client.get(path, params)
        response.content = response.content.strip()
        if format:
            self.assert_extended(response, format, 'object', limit)
        self.assert_status(response, [200, 204])
        return response

    def create_container(self, account, name, **meta):
        path = '/v1/%s/%s' %(account, name)
        response = self.client.put(path, **meta)
        response.content = response.content.strip()
        self.assert_status(response, [201, 202])
        return response

    def update_container_meta(self, account, name, **meta):
        path = '/v1/%s/%s' %(account, name)
        response = self.client.post(path, data={}, content_type='text/xml', follow=False, **meta)
        response.content = response.content.strip()
        self.assert_status(response, 202)
        return response

    def delete_container(self, account, container):
        path = '/v1/%s/%s' %(account, container)
        response = self.client.delete(path)
        response.content = response.content.strip()
        self.assert_status(response, [204, 409])
        return response

    def get_object_meta(self, account, container, name):
        path = '/v1/%s/%s/%s' %(account, container, name)
        response = self.client.head(path)
        response.content = response.content.strip()
        self.assert_status(response, 204)
        return response

    def get_object(self, account, container, name, exp_meta={}, **headers):
        path = '/v1/%s/%s/%s' %(account, container, name)
        response = self.client.get(path, **headers)
        response.content = response.content.strip()
        self.assert_status(response, [200, 206, 304, 412, 416])
        if response.status_code in [200, 206]:
            self.assert_headers(response, 'object')
        return response

    def upload_object(self, account, container, name, data, content_type='application/json', **headers):
        path = '/v1/%s/%s/%s' %(account, container, name)
        response = self.client.put(path, data, content_type, **headers)
        response.content = response.content.strip()
        self.assert_status(response, [201, 411, 422])
        if response.status_code == 201:
            self.assertTrue(response['Etag'])
        return response

    def copy_object(self, account, container, name, src, **headers):
        path = '/v1/%s/%s/%s' %(account, container, name)
        headers['HTTP_X_COPY_FROM'] = src
        response = self.client.put(path, **headers)
        response.content = response.content.strip()
        self.assert_status(response, 201)
        return response

    def move_object(self, account, container, name, src, **headers):
        path = '/v1/%s/%s/%s' % (account, container, name)
        headers['HTTP_X_MOVE_FROM'] = src
        response = self.client.put(path, **headers)
        response.content = response.content.strip()
        self.assert_status(response, 201)
        return response

    def update_object_meta(self, account, container, name, **headers):
        path = '/v1/%s/%s/%s' %(account, container, name)
        response = self.client.post(path, **headers)
        response.content = response.content.strip()
        self.assert_status(response, 202)
        return response

    def delete_object(self, account, container, name):
        path = '/v1/%s/%s/%s' %(account, container, name)
        response = self.client.delete(path)
        response.content = response.content.strip()
        self.assert_status(response, 204)
        return response

    def assert_headers(self, response, type, exp_meta={}):
        entities = ['Account', 'Container', 'Container-Object', 'Object']
        user_defined_meta = ['X-%s-Meta' %elem for elem in entities]
        headers = [item for item in response._headers.values()]
        system_headers = [h for h in headers if not h[0].startswith(tuple(user_defined_meta))]
        for h in system_headers:
            self.assertTrue(h[0] in self.headers[type])
            if exp_meta:
                self.assertEqual(h[1], exp_meta[h[0]])

    def assert_extended(self, response, format, type, size):
        self.assertEqual(response['Content-Type'].find(self.contentTypes[format]), 0)
        if format == 'xml':
            self.assert_xml(response, type, size)
        elif format == 'json':
            self.assert_json(response, type, size)

    def assert_json(self, response, type, size):
        convert = lambda s: s.lower()
        info = [convert(elem) for elem in self.extended[type]]
        data = json.loads(response.content)
        self.assertTrue(len(data) <= size)
        for item in info:
            for i in data:
                if 'subdir' in i.keys():
                    continue
                self.assertTrue(item in i.keys())

    def assert_xml(self, response, type, size):
        convert = lambda s: s.lower()
        info = [convert(elem) for elem in self.extended[type]]
        try:
            info.remove('content_encoding')
        except ValueError:
            pass
        xml = minidom.parseString(response.content)
        for item in info:
            nodes = xml.getElementsByTagName(item)
            self.assertTrue(nodes)
            self.assertTrue(len(nodes) <= size)
            

    def upload_os_file(self, account, container, fullpath, meta={}):
        try:
            f = open(fullpath, 'r')
            data = f.read()
            name = os.path.split(fullpath)[-1]
            return self.upload_data(account, container, name, data)    
        except IOError:
            return

    def upload_random_data(self, account, container, name, length=1024, meta={}):
        data = str(random.getrandbits(length))
        return self.upload_data(account, container, name, data, meta)

    def upload_data(self, account, container, name, data, meta={}):
        obj = {}
        obj['name'] = name
        try:
            obj['data'] = data
            obj['hash'] = compute_hash(obj['data'])
            meta.update({'HTTP_X_OBJECT_META_TEST':'test1',
                         'HTTP_ETAG':obj['hash']})
            meta['HTTP_CONTENT_TYPE'], enc = mimetypes.guess_type(name)
            if enc:
                meta['HTTP_CONTENT_TYPE'] = enc
            obj['meta'] = meta
            r = self.upload_object(account,
                               container,
                               obj['name'],
                               obj['data'],
                               meta['HTTP_CONTENT_TYPE'],
                               **meta)
            if r.status_code == 201:
                return obj
        except IOError:
            return

class ListContainers(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        #create some containers
        self.containers = ['apples', 'bananas', 'kiwis', 'oranges', 'pears']
        for item in self.containers:
            self.create_container(self.account, item)

    def tearDown(self):
        for c in get_content_splitted(self.list_containers(self.account)):
            response = self.delete_container(self.account, c)

    def test_list(self):
        #list containers
        response = self.list_containers(self.account)
        containers = get_content_splitted(response)
        self.assertEquals(self.containers, containers)

    #def test_list_204(self):
    #    response = self.list_containers('non-existing-account')
    #    self.assertEqual(response.status_code, 204)

    def test_list_with_limit(self):
        limit = 2
        response = self.list_containers(self.account, limit=limit)
        containers = get_content_splitted(response)
        self.assertEquals(len(containers), limit)
        self.assertEquals(self.containers[:2], containers)

    def test_list_with_marker(self):
        limit = 2
        marker = 'bananas'
        response = self.list_containers(self.account, limit=limit, marker=marker)
        containers =  get_content_splitted(response)
        i = self.containers.index(marker) + 1
        self.assertEquals(self.containers[i:(i+limit)], containers)
        
        marker = 'oranges'
        response = self.list_containers(self.account, limit=limit, marker=marker)
        containers = get_content_splitted(response)
        i = self.containers.index(marker) + 1
        self.assertEquals(self.containers[i:(i+limit)], containers)

    #def test_extended_list(self):
    #    self.list_containers(self.account, limit=3, format='xml')
    #    self.list_containers(self.account, limit=3, format='json')

    def test_list_json_with_marker(self):
        limit = 2
        marker = 'bananas'
        response = self.list_containers(self.account, limit=limit, marker=marker, format='json')
        containers = json.loads(response.content)
        self.assertEqual(containers[0]['name'], 'kiwis')
        self.assertEqual(containers[1]['name'], 'oranges')

    def test_list_xml_with_marker(self):
        limit = 2
        marker = 'oranges'
        response = self.list_containers(self.account, limit=limit, marker=marker, format='xml')
        xml = minidom.parseString(response.content)
        nodes = xml.getElementsByTagName('name')
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].childNodes[0].data, 'pears')

class AccountMetadata(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.containers = ['apples', 'bananas', 'kiwis', 'oranges', 'pears']
        for item in self.containers:
            self.create_container(self.account, item)

    def tearDown(self):
        for c in  get_content_splitted(self.list_containers(self.account)):
            self.delete_container(self.account, c)

    def test_get_account_meta(self):
        response = self.get_account_meta(self.account)
        r2 = self.list_containers(self.account)
        containers =  get_content_splitted(r2)
        self.assertEqual(response['X-Account-Container-Count'], str(len(containers)))
        size = 0
        for c in containers:
            r = self.get_container_meta(self.account, c)
            size = size + int(r['X-Container-Bytes-Used'])
        self.assertEqual(response['X-Account-Bytes-Used'], str(size))

    #def test_get_account_401(self):
    #    response = self.get_account_meta('non-existing-account')
    #    print response
    #    self.assertEqual(response.status_code, 401)

    def test_update_meta(self):
        meta = {'HTTP_X_ACCOUNT_META_TEST':'test', 'HTTP_X_ACCOUNT_META_TOST':'tost'}
        response = self.update_account_meta(self.account, **meta)
        response = self.get_account_meta(self.account)
        for k,v in meta.items():
            key = '-'.join(elem.capitalize() for elem in k.split('_')[1:])
            self.assertTrue(response[key])
            self.assertEqual(response[key], v)

    #def test_invalid_account_update_meta(self):
    #    with AssertInvariant(self.get_account_meta, self.account):
    #        meta = {'HTTP_X_ACCOUNT_META_TEST':'test', 'HTTP_X_ACCOUNT_META_TOST':'tost'}
    #        response = self.update_account_meta('non-existing-account', **meta)

class ListObjects(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.container = ['pears', 'apples']
        for c in self.container:
            self.create_container(self.account, c)
        self.obj = []
        for o in o_names[:8]:
            self.obj.append(self.upload_random_data(self.account,
                                                    self.container[0],
                                                    o))
        for o in o_names[8:]:
            self.obj.append(self.upload_random_data(self.account,
                                                    self.container[1],
                                                    o))

    def tearDown(self):
        for c in self.container:
            self.delete_container_recursively(c)

    def delete_container_recursively(self, c):
        for obj in get_content_splitted(self.list_objects(self.account, c)):
            self.delete_object(self.account, c, obj)
        self.delete_container(self.account, c)

    def test_list_objects(self):
        response = self.list_objects(self.account, self.container[0])
        objects = get_content_splitted(response)
        l = [elem['name'] for elem in self.obj[:8]]
        l.sort()
        self.assertEqual(objects, l)

    def test_list_objects_with_limit_marker(self):
        response = self.list_objects(self.account, self.container[0], limit=2)
        objects = get_content_splitted(response)
        l = [elem['name'] for elem in self.obj[:8]]
        l.sort()
        self.assertEqual(objects, l[:2])
        
        markers = ['How To Win Friends And Influence People.pdf',
                   'moms_birthday.jpg']
        limit = 4
        for m in markers:
            response = self.list_objects(self.account, self.container[0], limit=limit, marker=m)
            objects = get_content_splitted(response)
            l = [elem['name'] for elem in self.obj[:8]]
            l.sort()
            start = l.index(m) + 1
            end = start + limit
            end = len(l) >= end and end or len(l)
            self.assertEqual(objects, l[start:end])

    def test_list_pseudo_hierarchical_folders(self):
        response = self.list_objects(self.account, self.container[1], prefix='photos', delimiter='/')
        objects = get_content_splitted(response)
        self.assertEquals(['photos/animals/', 'photos/me.jpg', 'photos/plants/'], objects)
        
        response = self.list_objects(self.account, self.container[1], prefix='photos/animals', delimiter='/')
        objects = get_content_splitted(response)
        self.assertEquals(['photos/animals/cats/', 'photos/animals/dogs/'], objects)
        
        response = self.list_objects(self.account, self.container[1], path='photos')
        objects = get_content_splitted(response)
        self.assertEquals(['photos/me.jpg'], objects)

    def test_extended_list_json(self):
        response = self.list_objects(self.account, self.container[1], format='json', limit=2, prefix='photos/animals', delimiter='/')
        objects = json.loads(response.content)
        self.assertEqual(objects[0]['subdir'], 'photos/animals/cats/')
        self.assertEqual(objects[1]['subdir'], 'photos/animals/dogs/')

    def test_extended_list_xml(self):
        response = self.list_objects(self.account, self.container[1], format='xml', limit=4, prefix='photos', delimiter='/')
        xml = minidom.parseString(response.content)
        dirs = xml.getElementsByTagName('subdir')
        self.assertEqual(len(dirs), 2)
        self.assertEqual(dirs[0].attributes['name'].value, 'photos/animals/')
        self.assertEqual(dirs[1].attributes['name'].value, 'photos/plants/')
        
        objects = xml.getElementsByTagName('name')
        self.assertEqual(len(objects), 1)
        self.assertEqual(objects[0].childNodes[0].data, 'photos/me.jpg')

    def test_list_using_meta(self):
        meta = {'HTTP_X_OBJECT_META_QUALITY':'aaa'}
        for o in self.obj[:2]:
            r = self.update_object_meta(self.account,
                                    self.container[0],
                                    o['name'],
                                    **meta)
        meta = {'HTTP_X_OBJECT_META_STOCK':'true'}
        for o in self.obj[3:5]:
            r = self.update_object_meta(self.account,
                                    self.container[0],
                                    o['name'],
                                    **meta)
            
        r = self.list_objects(self.account,
                          self.container[0],
                          meta='Quality')
        self.assertEqual(r.status_code, 200)
        obj = get_content_splitted(r)
        self.assertEqual(len(obj), 2)
        
        # test case insensitive
        r = self.list_objects(self.account,
                          self.container[0],
                          meta='quality')
        self.assertEqual(r.status_code, 200)
        obj = get_content_splitted(r)
        self.assertEqual(len(obj), 2)
        
        # test multiple matches
        r = self.list_objects(self.account,
                          self.container[0],
                          meta='Quality, Stock')
        self.assertEqual(r.status_code, 200)
        obj = get_content_splitted(r)
        self.assertEqual(len(obj), 4)
        
        # test non 1-1 multiple match
        r = self.list_objects(self.account,
                          self.container[0],
                          meta='Quality, aaaa')
        self.assertEqual(r.status_code, 200)
        obj = get_content_splitted(r)
        self.assertEqual(len(obj), 2)
        

class ContainerMeta(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.container = 'apples'
        self.create_container(self.account, self.container)

    def tearDown(self):
        for o in self.list_objects(self.account, self.container):
            self.delete_object(self.account, self.container, o)
        self.delete_container(self.account, self.container)
    
    def test_get_meta(self):
        headers = {'HTTP_X_OBJECT_META_TRASH':'true'}
        t1 = datetime.datetime.utcnow()
        o = self.upload_random_data(self.account,
                                self.container,
                                'McIntosh.jpg',
                                meta=headers)
        if o:
            r = self.get_container_meta(self.account,
                                        self.container)
            self.assertEqual(r['X-Container-Object-Count'], '1')
            self.assertEqual(r['X-Container-Bytes-Used'], str(len(o['data'])))
            t2 = datetime.datetime.strptime(r['Last-Modified'], DATE_FORMATS[2])
            delta = (t2 - t1)
            threashold = datetime.timedelta(seconds=1) 
            self.assertTrue(delta < threashold)
            self.assertTrue(r['X-Container-Object-Meta'])
            self.assertTrue('Trash' in r['X-Container-Object-Meta'])

    def test_update_meta(self):
        meta = {'HTTP_X_CONTAINER_META_TEST':'test33', 'HTTP_X_CONTAINER_META_TOST':'tost22'}
        response = self.update_container_meta(self.account, self.container, **meta)
        response = self.get_container_meta(self.account, self.container)
        for k,v in meta.items():
            key = '-'.join(elem.capitalize() for elem in k.split('_')[1:])
            self.assertTrue(response[key])
            self.assertEqual(response[key], v)

class CreateContainer(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.containers = ['c1', 'c2']

    def tearDown(self):
        for c in self.containers:
            r = self.delete_container(self.account, c)

    def test_create(self):
        response = self.create_container(self.account, self.containers[0])
        if response.status_code == 201:
            response = self.list_containers(self.account)
            self.assertTrue(self.containers[0] in get_content_splitted(response))
            r = self.get_container_meta(self.account, self.containers[0])
            self.assertEqual(r.status_code, 204)

    def test_create_twice(self):
        response = self.create_container(self.account, self.containers[0])
        if response.status_code == 201:
            self.assertTrue(self.create_container(self.account, self.containers[0]).status_code, 202)

class DeleteContainer(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.containers = ['c1', 'c2']
        for c in self.containers:
            self.create_container(self.account, c)
        self.upload_random_data(self.account,
                                self.containers[1],
                                'nice.jpg')

    def tearDown(self):
        for c in self.containers:
            for o in get_content_splitted(self.list_objects(self.account, c)):
                self.delete_object(self.account, c, o)
            self.delete_container(self.account, c)

    def test_delete(self):
        r = self.delete_container(self.account, self.containers[0])
        self.assertEqual(r.status_code, 204)

    def test_delete_non_empty(self):
        r = self.delete_container(self.account, self.containers[1])
        self.assertNonEmpty(r)

    def test_delete_invalid(self):
        self.assertItemNotFound(self.delete_container(self.account, 'c3'))

class GetObjects(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.containers = ['c1', 'c2']
        #create some containers
        for c in self.containers:
            self.create_container(self.account, c)
        
        #upload a file
        self.objects = []
        self.objects.append(self.upload_os_file(self.account,
                            self.containers[1],
                            './api/tests.py'))
        self.objects.append(self.upload_os_file(self.account,
                            self.containers[1],
                            'settings.py'))

    def tearDown(self):
        for c in self.containers:
            for o in get_content_splitted(self.list_objects(self.account, c)):
                self.delete_object(self.account, c, o)
            self.delete_container(self.account, c)

    def test_get(self):
        #perform get
        r = self.get_object(self.account,
                            self.containers[1],
                            self.objects[0]['name'],
                            self.objects[0]['meta'])
        #assert success
        self.assertEqual(r.status_code, 200)

    def test_get_invalid(self):
        r = self.get_object(self.account,
                            self.containers[0],
                            self.objects[0]['name'])
        self.assertItemNotFound(r)

    def test_get_partial(self):
        #perform get with range
        headers = {'HTTP_RANGE':'bytes=0-499'}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert successful partial content
        self.assertEqual(r.status_code, 206)
        
        #assert content length
        self.assertEqual(int(r['Content-Length']), 500)
        
        #assert content
        self.assertEqual(self.objects[0]['data'][:500], r.content)

    def test_get_final_500(self):
        #perform get with range
        headers = {'HTTP_RANGE':'bytes=-500'}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert successful partial content
        self.assertEqual(r.status_code, 206)
        
        #assert content length
        self.assertEqual(int(r['Content-Length']), 500)
        
        #assert content
        self.assertTrue(self.objects[0]['data'][-500:], r.content)

    def test_get_rest(self):
        #perform get with range
        offset = len(self.objects[0]['data']) - 500
        headers = {'HTTP_RANGE':'bytes=%s-' %offset}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert successful partial content
        self.assertEqual(r.status_code, 206)
        
        #assert content length
        self.assertEqual(int(r['Content-Length']), 500)
        
        #assert content
        self.assertTrue(self.objects[0]['data'][-500:], r.content)
        
    def test_get_range_not_satisfiable(self):
        #perform get with range
        offset = len(self.objects[0]['data']) + 1
        headers = {'HTTP_RANGE':'bytes=0-%s' %offset}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert Range Not Satisfiable
        self.assertEqual(r.status_code, 416)

    def test_multiple_range(self):
        #perform get with multiple range
        ranges = ['0-499', '-500', '1000-']
        headers = {'HTTP_RANGE' : 'bytes=%s' % ','.join(ranges)}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        # assert partial content
        self.assertEqual(r.status_code, 206)
        
        # assert Content-Type of the reply will be multipart/byteranges
        self.assertTrue(r['Content-Type'])
        content_type_parts = r['Content-Type'].split()
        self.assertEqual(content_type_parts[0], ('multipart/byteranges;'))
        
        boundary = '--%s' %content_type_parts[1].split('=')[-1:][0]
        cparts = r.content.split(boundary)[1:-1]
        
        # assert content parts are exactly 2
        self.assertEqual(len(cparts), len(ranges))
        
        # for each content part assert headers
        i = 0
        for cpart in cparts:
            content = cpart.split('\r\n')
            headers = content[1:3]
            content_range = headers[0].split(': ')
            self.assertEqual(content_range[0], 'Content-Range')
            
            r = ranges[i].split('-')
            if not r[0] and not r[1]:
                pass
            elif not r[0]:
                start = len(self.objects[0]['data']) - int(r[1])
                end = len(self.objects[0]['data'])
            elif not r[1]:
                start = int(r[0])
                end = len(self.objects[0]['data'])
            else:
                start = int(r[0])
                end = int(r[1]) + 1
            fdata = self.objects[0]['data'][start:end]
            sdata = '\r\n'.join(content[4:-1])
            self.assertEqual(len(fdata), len(sdata))
            self.assertEquals(fdata, sdata)
            i+=1

    def test_multiple_range_not_satisfiable(self):
        #perform get with multiple range
        out_of_range = len(self.objects[0]['data']) + 1
        ranges = ['0-499', '-500', '%d-' %out_of_range]
        headers = {'HTTP_RANGE' : 'bytes=%s' % ','.join(ranges)}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        # assert partial content
        self.assertEqual(r.status_code, 416)

    def test_get_with_if_match(self):
        #perform get with If-Match
        headers = {'HTTP_IF_MATCH':self.objects[0]['hash']}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        #assert get success
        self.assertEqual(r.status_code, 200)
        
        #assert response content
        self.assertEqual(self.objects[0]['data'].strip(), r.content.strip())

    def test_get_with_if_match_star(self):
        #perform get with If-Match *
        headers = {'HTTP_IF_MATCH':'*'}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        #assert get success
        self.assertEqual(r.status_code, 200)
        
        #assert response content
        self.assertEqual(self.objects[0]['data'].strip(), r.content.strip())

    def test_get_with_multiple_if_match(self):
        #perform get with If-Match
        etags = [i['hash'] for i in self.objects if i]
        etags = ','.join('"%s"' % etag for etag in etags)
        headers = {'HTTP_IF_MATCH':etags}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        #assert get success
        self.assertEqual(r.status_code, 200)
        
        #assert response content
        self.assertEqual(self.objects[0]['data'].strip(), r.content.strip())

    def test_if_match_precondition_failed(self):
        #perform get with If-Match
        headers = {'HTTP_IF_MATCH':'123'}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert precondition failed 
        self.assertEqual(r.status_code, 412)

    def test_if_none_match(self):
        #perform get with If-Match
        headers = {'HTTP_IF_NONE_MATCH':'123'}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert get success
        self.assertEqual(r.status_code, 200)

    def test_if_none_match(self):
        #perform get with If-Match *
        headers = {'HTTP_IF_NONE_MATCH':'*'}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert get success
        self.assertEqual(r.status_code, 304)
        
    def test_if_none_match_not_modified(self):
        #perform get with If-Match
        headers = {'HTTP_IF_NONE_MATCH':'%s' %self.objects[0]['hash']}
        r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
        
        #assert not modified
        self.assertEqual(r.status_code, 304)
        self.assertEqual(r['ETag'], self.objects[0]['hash'])
        
    def test_get_with_if_modified_since(self):
        t = datetime.datetime.utcnow()
        t2 = t - datetime.timedelta(minutes=10)
        
        #modify the object
        self.upload_object(self.account,
                           self.containers[1],
                           self.objects[0]['name'],
                           self.objects[0]['data'][:200])
        
        for f in DATE_FORMATS:
            past = t2.strftime(f)
            
            headers = {'HTTP_IF_MODIFIED_SINCE':'%s' %past}
            r = self.get_object(self.account,
                        self.containers[1],
                        self.objects[0]['name'],
                        **headers)
            
            #assert get success
            self.assertEqual(r.status_code, 200)
            
    def test_get_modified_since_invalid_date(self):
        headers = {'HTTP_IF_MODIFIED_SINCE':''}
        r = self.get_object(self.account,
                    self.containers[1],
                    self.objects[0]['name'],
                    **headers)
        
        #assert get success
        self.assertEqual(r.status_code, 200)

    def test_get_not_modified_since(self):
        now = datetime.datetime.utcnow()
        since = now + datetime.timedelta(1)
        
        for f in DATE_FORMATS:
            headers = {'HTTP_IF_MODIFIED_SINCE':'%s' %since.strftime(f)}
            r = self.get_object(self.account,
                                self.containers[1],
                                self.objects[0]['name'],
                                **headers)
            
            #assert not modified
            self.assertEqual(r.status_code, 304)

    def test_get_with_if_unmodified_since(self):
        return

class UploadObject(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.container = 'c1'
        self.create_container(self.account, self.container)
        
        self.src = os.path.join('.', 'api', 'tests.py')
        self.dest = os.path.join('.', 'api', 'chunked_update_test_file')
        create_chunked_update_test_file(self.src, self.dest)

    def tearDown(self):
        for o in get_content_splitted(self.list_objects(self.account, self.container)):
            self.delete_object(self.account, self.container, o)
        self.delete_container(self.account, self.container)
        
        # delete test file
        os.remove(self.dest)
        
    def test_upload(self):
        filename = 'tests.py'
        fullpath = os.path.join('.', 'api', filename) 
        f = open(fullpath, 'r')
        data = f.read()
        hash = compute_hash(data)
        meta={'HTTP_ETAG':hash,
              'HTTP_X_OBJECT_MANIFEST':123,
              'HTTP_X_OBJECT_META_TEST':'test1'
              }
        meta['HTTP_CONTENT_TYPE'], meta['HTTP_CONTENT_ENCODING'] = mimetypes.guess_type(fullpath)
        r = self.upload_object(self.account,
                               self.container,
                               filename,
                               data,
                               content_type=meta['HTTP_CONTENT_TYPE'],
                               **meta)
        self.assertEqual(r.status_code, 201)
        r = self.get_object_meta(self.account, self.container, filename)
        self.assertTrue(r['X-Object-Meta-Test'])
        self.assertEqual(r['X-Object-Meta-Test'], meta['HTTP_X_OBJECT_META_TEST'])
        
        #assert uploaded content
        r = self.get_object(self.account, self.container, filename)
        self.assertEqual(os.path.getsize(fullpath), int(r['Content-Length']))
        self.assertEqual(data.strip(), r.content.strip())

    def test_upload_unprocessable_entity(self):
        filename = 'tests.py'
        fullpath = os.path.join('.', 'api', filename) 
        f = open(fullpath, 'r')
        data = f.read()
        meta={'HTTP_ETAG':'123',
              'HTTP_X_OBJECT_MANIFEST':123,
              'HTTP_X_OBJECT_META_TEST':'test1'
              }
        meta['HTTP_CONTENT_TYPE'], meta['HTTP_CONTENT_ENCODING'] = mimetypes.guess_type(fullpath)
        r = self.upload_object(self.account,
                               self.container,
                               filename,
                               data,
                               content_type = meta['HTTP_CONTENT_TYPE'],
                               **meta)
        self.assertEqual(r.status_code, 422)
        
    def test_chucked_update(self):
        objname = os.path.split(self.src)[-1:][0]
        f = open(self.dest, 'r')
        data = f.read()
        meta = {}
        meta['HTTP_CONTENT_TYPE'], meta['HTTP_CONTENT_ENCODING'] = mimetypes.guess_type(objname)
        meta.update({'HTTP_TRANSFER_ENCODING':'chunked'})
        r = self.upload_object(self.account,
                               self.container,
                               objname,
                               data,
                               content_type = 'plain/text',
                               **meta)
        self.assertEqual(r.status_code, 201)
        
        r = self.get_object(self.account,
                            self.container,
                            objname)
        uploaded_data = r.content
        f = open(self.src, 'r')
        actual_data = f.read()
        self.assertEqual(actual_data, uploaded_data)

class CopyObject(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.containers = ['c1', 'c2']
        for c in self.containers:
            self.create_container(self.account, c)
        self.obj = self.upload_os_file(self.account,
                            self.containers[0],
                            './api/tests.py')

    def tearDown(self):
        for c in self.containers:
            for o in get_content_splitted(self.list_objects(self.account, c)):
                self.delete_object(self.account, c, o)
            self.delete_container(self.account, c)

    def test_copy(self):
        with AssertInvariant(self.get_object_meta, self.account, self.containers[0], self.obj['name']):
            #perform copy
            meta = {'HTTP_X_OBJECT_META_TEST':'testcopy'}
            src_path = os.path.join('/', self.containers[0], self.obj['name'])
            r = self.copy_object(self.account,
                             self.containers[0],
                             'testcopy',
                             src_path,
                             **meta)
            #assert copy success
            self.assertEqual(r.status_code, 201)
            
            #assert access the new object
            r = self.get_object_meta(self.account,
                                     self.containers[0],
                                     'testcopy')
            self.assertTrue(r['X-Object-Meta-Test'])
            self.assertTrue(r['X-Object-Meta-Test'], 'testcopy')
            
            #assert etag is the same
            self.assertEqual(r['ETag'], self.obj['hash'])
            
            #assert src object still exists
            r = self.get_object_meta(self.account, self.containers[0], self.obj['name'])
            self.assertEqual(r.status_code, 204)

    def test_copy_from_different_container(self):
        with AssertInvariant(self.get_object_meta,
                             self.account,
                             self.containers[0],
                             self.obj['name']):
            meta = {'HTTP_X_OBJECT_META_TEST':'testcopy'}
            src_path = os.path.join('/', self.containers[0], self.obj['name'])
            r = self.copy_object(self.account,
                             self.containers[1],
                             'testcopy',
                             src_path,
                             **meta)
            self.assertEqual(r.status_code, 201)
            
            # assert updated metadata
            r = self.get_object_meta(self.account,
                                     self.containers[1],
                                     'testcopy')
            self.assertTrue(r['X-Object-Meta-Test'])
            self.assertTrue(r['X-Object-Meta-Test'], 'testcopy')
            
            #assert src object still exists
            r = self.get_object_meta(self.account, self.containers[0], self.obj['name'])
            self.assertEqual(r.status_code, 204)

    def test_copy_invalid(self):
        #copy from invalid object
        meta = {'HTTP_X_OBJECT_META_TEST':'testcopy'}
        r = self.copy_object(self.account,
                         self.containers[1],
                         'testcopy',
                         os.path.join('/', self.containers[0], 'test.py'),
                         **meta)
        self.assertItemNotFound(r)
        
        
        #copy from invalid container
        meta = {'HTTP_X_OBJECT_META_TEST':'testcopy'}
        src_path = os.path.join('/', self.containers[1], self.obj['name'])
        r = self.copy_object(self.account,
                         self.containers[1],
                         'testcopy',
                         src_path,
                         **meta)
        self.assertItemNotFound(r)

class MoveObject(CopyObject):
    def test_move(self):
        #perform move
        meta = {'HTTP_X_OBJECT_META_TEST':'testcopy'}
        src_path = os.path.join('/', self.containers[0], self.obj['name'])
        r = self.move_object(self.account,
                         self.containers[0],
                         'testcopy',
                         src_path,
                         **meta)
        #assert successful move
        self.assertEqual(r.status_code, 201)
        
        #assert updated metadata
        r = self.get_object_meta(self.account,
                                 self.containers[0],
                                 'testcopy')
        self.assertTrue(r['X-Object-Meta-Test'])
        self.assertTrue(r['X-Object-Meta-Test'], 'testcopy')
        
        #assert src object no more exists
        r = self.get_object_meta(self.account, self.containers[0], self.obj['name'])
        self.assertItemNotFound(r)

class UpdateObjectMeta(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.containers = ['c1', 'c2']
        for c in self.containers:
            self.create_container(self.account, c)
        self.obj = self.upload_os_file(self.account,
                                       self.containers[0],
                                       './api/tests.py')

    def tearDown(self):
        for c in self.containers:
            for o in get_content_splitted(self.list_objects(self.account, c)):
                self.delete_object(self.account, c, o)
            self.delete_container(self.account, c)

    def test_update(self):
        #perform update metadata
        more = {'HTTP_X_OBJECT_META_FOO':'foo',
                'HTTP_X_OBJECT_META_BAR':'bar'}
        r = self.update_object_meta(self.account,
                                self.containers[0],
                                self.obj['name'],
                                **more)
        #assert request accepted
        self.assertEqual(r.status_code, 202)
        
        #assert old metadata are still there
        r = self.get_object_meta(self.account, self.containers[0], self.obj['name'])
        self.assertTrue('X-Object-Meta-Test' not in r.items())
        
        #assert new metadata have been updated
        for k,v in more.items():
            key = '-'.join(elem.capitalize() for elem in k.split('_')[1:])
            self.assertTrue(r[key])
            self.assertTrue(r[key], v)

class DeleteObject(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.account = 'test'
        self.containers = ['c1', 'c2']
        for c in self.containers:
            self.create_container(self.account, c)
        self.obj = self.upload_os_file(self.account,
                            self.containers[0],
                            './api/tests.py')

    def tearDown(self):
        for c in self.containers:
            for o in get_content_splitted(self.list_objects(self.account, c)):
                self.delete_object(self.account, c, o)
            self.delete_container(self.account, c)

    def test_delete(self):
        #perform delete object
        r = self.delete_object(self.account, self.containers[0], self.obj['name'])
        
        #assert success
        self.assertEqual(r.status_code, 204)
        
    def test_delete_invalid(self):
        #perform delete object
        r = self.delete_object(self.account, self.containers[1], self.obj['name'])
        
        #assert failure
        self.assertItemNotFound(r)

class AssertInvariant(object):
    def __init__(self, callable, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        self.items = self.callable(*self.args, **self.kwargs).items()
        return self.items

    def __exit__(self, type, value, tb):
        items = self.callable(*self.args, **self.kwargs).items()
        assert self.items == items

def get_content_splitted(response):
    if response:
        return response.content.split('\n')

def compute_hash(data):
    md5 = hashlib.md5()
    offset = 0
    md5.update(data)
    return md5.hexdigest().lower()

def create_chunked_update_test_file(src, dest):
    fr = open(src, 'r')
    fw = open(dest, 'w')
    data = fr.readline()
    while data:
        fw.write(hex(len(data)))
        fw.write('\r\n')
        fw.write(data)
        data = fr.readline()
    fw.write(hex(0))
    fw.write('\r\n')

o_names = ['kate.jpg',
           'kate_beckinsale.jpg',
           'How To Win Friends And Influence People.pdf',
           'moms_birthday.jpg',
           'poodle_strut.mov',
           'Disturbed - Down With The Sickness.mp3',
           'army_of_darkness.avi',
           'the_mad.avi',
           'photos/animals/dogs/poodle.jpg',
           'photos/animals/dogs/terrier.jpg',
           'photos/animals/cats/persian.jpg',
           'photos/animals/cats/siamese.jpg',
           'photos/plants/fern.jpg',
           'photos/plants/rose.jpg',
           'photos/me.jpg']