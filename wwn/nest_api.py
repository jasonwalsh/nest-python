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
import urllib2
import requests

from errors import APIError, error_result, get_error_msg_help
from settings import nest_api_url


def get_device(token, device_type, device_id):
    api_path = "{0}/devices/{1}/{2}".format(nest_api_url, device_type, device_id)
    data = get_data(token, api_path)
    device = data.get("results") if data else None
    return device


def get_data(token, api_endpoint=nest_api_url):
    headers = {
        'Authorization': "Bearer {0}".format(token),
    }
    req = urllib2.Request(api_endpoint, None, headers)
    try:
        response = urllib2.urlopen(req)

    except urllib2.HTTPError as err:
        # send error message to client
        json_err = err.read()
        print "get_data error occurred: ", json_err
        raise apierr_from_json(err.code, json_err)

    except Exception as ex:
        # send error message to client
        print "Error: ", ex
        raise apierr_from_msg(500, "An error occurred connecting to the Nest API.")

    data = json.loads(response.read())

    return {"results": data}


def update(token, update_path, data):
    headers = {
        'Authorization': "Bearer {0}".format(token),
        'Content-Type': 'application/json'
    }
    api_path = "{0}/{1}".format(nest_api_url, update_path)
    print "update: api_path: ", api_path
    response = requests.put(api_path, data=data, headers=headers, allow_redirects=False)
    resp_code = response.status_code

    if resp_code == 200:
        return True

    elif resp_code == 307:
        # option: cache redirect_url to reduce requests to Nest API
        redirect_url = response.headers['Location']
        print "redirect_url: ", redirect_url
        next_resp = requests.put(redirect_url, data=data, headers=headers, allow_redirects=False)
        next_resp_code = next_resp.status_code
        if next_resp_code == 200:
            return True
        else:
            # send error message to client
            raise apierr_from_json(next_resp_code, next_resp.content)

    else:
        # send error message to client
        raise apierr_from_json(resp_code, response.content)


def apierr_from_json(code, json_msg):
    """ Retrieve the error message field from JSON sent from the Nest API.
    * Example: HTTP Status Code: 400 Bad Request, HTTP response (message will be in JSON format):
    {
        "error": "Temperature '$temp' is in wrong format",
        "type": "https://console.developers.nest.com/documentation/cloud/error-messages#format-error",
        "message": "Temperature '$temp' is in wrong format",
        "instance": "31441a94-ed26-11e4-90ec-1681e6b88ec1",
        "details": {
            "field_name": "$temp"
        }
    }

    See Nest API Error messages (https://developers.nest.com/documentation/cloud/error-messages) for more examples.
    """
    try:
        respjson = json.loads(json_msg)
        errmsg = respjson.get("message")
    except Exception as e:
        print "Exception reading error message as json: ", e
        errmsg = ''

    return apierr_from_msg(code, errmsg)

def apierr_from_msg(code, err_msg="Error"):
    # get additional message (not from the API), for next steps or more details.
    help_msg = get_error_msg_help(code, '')

    return APIError(code, error_result("{0}: {1}. {2}".format(str(code), err_msg, help_msg)))
