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

import unittest
import urllib2

import app
from sample import auth
from errors import APIError, error_result

dummy_accesstoken_val = '123-test'
dummy_authcode_val = '123-test'

class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['SECRET_KEY'] = 'secret-123'
        self.app = app.app.test_client()

    def tearDown(self):
        app.app.config['TESTING'] = False
        self.app = None

    def test_index(self):
        response = self.app.get('/', follow_redirects=True)
        print "response.status ", response.status
        self.assertEqual(response.status, "200 OK")

    def test_login(self):
        response = self.app.get('/login')
        print "response.status ", response.status
        self.assertEqual(response.status, "302 FOUND")
        redirect_url = response.headers['Location']
        print "redirect_url: ", redirect_url
        self.assertEqual(redirect_url, auth.get_url())

    def test_logout(self):
        response = self.app.get('/logout', follow_redirects=True)
        print "response.status ", response.status
        self.assertEqual(response.status, "200 OK")

    def test_callback(self):
        # get authorization code to exchange for an access token
        authorization_code = dummy_authcode_val # request.args.get("code")
        token = None
        try:
            auth.get_access(authorization_code)
            token = auth.get_token()
        except urllib2.HTTPError as err:
            # expecting error message in JSON format, such as
            # {"error":"oauth2_error","error_description":"authorization code not found","instance_id":"65671693-1037-4d4e-bdab-f4852fe8aed0"}
            json_err = err.read()
            print "get_data error occurred: ", json_err

        self.assertIsNone(token, "Token not returned using dummy authorization code")


    """
    def test_process_api_err(self):
        with self.app.test_request_context():
            auth.store_token(dummy_accesstoken_val)
        try:
            response = self.app.get('/apicontent', follow_redirects=True)
        except APIError as err:
            err_result =  app.process_api_err(err)
            print "process_api_err msg: ", err_result
    """

    def test_apicontent(self):
        response = self.app.get('/apicontent', follow_redirects=True)
        print "response.status ", response.status
        self.assertEqual(response.status, "400 BAD REQUEST")

    def test_camera_imgs(self):
        response = self.app.get('/camera_imgs', follow_redirects=True)
        print "response.status ", response.status
        self.assertEqual(response.status, "200 OK")

    def test_thermostat_hist(self):
        response = self.app.get('/thermostat_hist', follow_redirects=True)
        print "response.status ", response.status
        self.assertEqual(response.status, "200 OK")

    def test_apiupdate(self):
        response = self.app.put('/apiupdate/structures/1234', follow_redirects=True)
        print "response.status ", response.status
        self.assertNotEqual(response.status, "200 OK")

if __name__ == '__main__':
    unittest.main()
