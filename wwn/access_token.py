#!/usr/bin/python
#
# Copyright 2017 Nest Labs Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import urllib
import urllib2

import settings

nest_auth_url = settings.nest_auth_url
nest_access_token_url = settings.nest_access_token_url
nest_api_root_url = settings.nest_api_root_url
nest_tokens_path = settings.nest_tokens_path

product_id = settings.product_id
product_secret = settings.product_secret


def get_access_token(authorization_code):
    data = urllib.urlencode({
        'client_id': product_id,
        'client_secret': product_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code'
    })
    req = urllib2.Request(nest_access_token_url, data)
    response = urllib2.urlopen(req)
    data = json.loads(response.read())
    return data['access_token']


def delete_access_token(token):
    path = nest_tokens_path + token
    req = urllib2.Request(nest_api_root_url + path, None)
    req.get_method = lambda: "DELETE"
    response = urllib2.urlopen(req)
    resp_code = response.getcode()
    print "deleted token, response code: ", resp_code
    return resp_code


def authorization_url():
    query = urllib.urlencode({
        'client_id': product_id,
        'state': 'STATE'
    })
    return "{0}?{1}".format(nest_auth_url, query)
