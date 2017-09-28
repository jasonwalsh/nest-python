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

from flask import session

from wwn import access_token
import data_store


def get_url():
    return access_token.authorization_url()


def get_access(authorization_code):
    token = access_token.get_access_token(authorization_code)
    store_token(token)


def remove_access():
    """ Product has correctly implemented deauth API when disconnecting or logging out.

     When the user requests to log out, deauthorize their token using the Nest
     deauthorization API then destroy their local session and cookies.
     See https://goo.gl/f2kfmv for more information.
    """
    token = fetch_token()
    if token:
        # delete user token using the Nest API
        try:
            access_token.delete_access_token(token)
        except Exception as ex:
            print "Error deleting access token: ", ex

        # delete token and user data from persistent storage and cache
        delete_cached_token()
        data_store.delete_user_data()

    else:
        print 'Not signed in.'


def get_token():
    return fetch_token()


def fetch_token():
    if session is not None and "token" in session:
        return session["token"]
    return None


def store_token(token):
    session["token"] = token


def delete_cached_token():
    session["token"] = None
