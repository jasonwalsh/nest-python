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

from flask import Flask, request, redirect, url_for, render_template, jsonify

from sample import views, auth, data_store
from errors import APIError, error_result
from wwn import nest_data as models, nest_api as api, port as wwn_port

app = Flask(__name__)

app.debug = False
app.threaded = False
app.secret_key = "test"
port = wwn_port
host = '0.0.0.0'

next_route = 'index' # view will depend on authorization (see index route below)


@app.route('/')
def index():
    # if not authorized show login/auth view
    if not auth.get_token():
        return render_template('index.html')

    # show application view
    return render_template('application.html', has_token=True)


@app.route('/login')
def login():
    # Redirect to authorization page
    return redirect(auth.get_url())


@app.route('/callback')
def callback():
    # get authorization code to exchange for an access token
    authorization_code = request.args.get("code")
    auth.get_access(authorization_code)
    return redirect(url_for(next_route))


@app.route('/logout')
def logout():
    """ Product handles logout/deauthorization, reverting to a disconnected state and removing all Nest
    user data, then redirects to enable a new oauth2 flow.
    """
    auth.remove_access()
    return redirect(url_for(next_route))


@app.route('/apicontent', methods=['GET'])
def apicontent():
    """ Checks for changes to current data to find out if some cached user data should be deleted.
    Returns content to be presented in client.
    """
    token = auth.get_token()
    if not token:
        print "missing token, return 400"
        return "", 400
    try:
        data = api.get_data(token)
    except APIError as err:
        return process_api_err(err)

    nestData = models.NestData(data)

    # compare data from last request, store device data for views, and delete data when required
    diff_list = data_store.process_data_changes(nestData)
    print "difference = ", diff_list

    # Verify the Nest account has at least one authorized structure in case it got deleted after authorizing it
    # (applies to new multi-structure authorization)
    if not nestData.has_structures():
        return jsonify({"error": "There are no authorized structures found.  Please re-authorize."})

    apicontent = views.get_api_content(request, nestData, diff_list)
    return jsonify(apicontent)


@app.route('/camera_imgs', methods=['GET'])
@app.route('/camera_imgs/<string:camera_id>', methods=['GET'])
def camera_imgs(camera_id=None, cache_ok=True):
    token = auth.get_token()
    if token == "":
        print "missing token, return 400"
        return "", 400

    if not camera_id:
        return jsonify({"error": 'Missing parameters'})

    device = None
    if cache_ok:
        print 'camera_imgs: try to get camera from cache (session) from previous poll request'
        device = data_store.get_device('cameras', camera_id)

    if not cache_ok or not device:
        print 'camera_imgs: get camera from new api request'
        try:
            device = api.get_device(token, 'cameras', camera_id)
        except APIError as err:
            return process_api_err(err)

    if not device:
        return jsonify({"error": "The camera was not found."})

    contents = views.get_camera_imgs(camera_id, device)
    return jsonify(contents)


@app.route('/thermostat_hist', methods=['GET'])
@app.route('/thermostat_hist/<string:thermostat_id>', methods=['GET'])
def thermostat_hist(thermostat_id=None, cache_ok=True):
    token = auth.get_token()
    if token == "":
        print "missing token, return 400"
        return "", 400

    if not thermostat_id:
        return jsonify({"error": 'Missing parameters'})

    device = None
    if cache_ok:
        print 'thermostat_hist: try to get thermostat from cache (session) from previous poll request'
        device = data_store.get_device('thermostats', thermostat_id)

    if not cache_ok or not device:
        print 'thermostat_hist: get thermostat from new api request'
        try:
            device = api.get_device(token, 'thermostats', thermostat_id)
        except APIError as err:
            return process_api_err(err)

    if not device:
        return jsonify({"error": "The thermostat was not found"})

    contents = views.get_thermostat_hist(thermostat_id, device)
    return jsonify(contents)


@app.route('/apiupdate/<path:update_path>', methods=['POST'])
def apiupdate(update_path=None):
    token = auth.get_token()
    if token == "":
        print "missing token, return 400"
        return "", 400

    data = views.convert_form(request)
    try:
        result = api.update(token, update_path, data)
    except APIError as err:
        return process_api_err(err)

    if result == True:
        return jsonify({"info": "API data was successfully updated."})
    else:
        return jsonify({"error": "Unknown error. API data was not updated."})


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error_result('404 - Page not found'))


@app.errorhandler(500)
def server_error(e):
    return jsonify(error_result('500 - Server error'))


def process_api_err(err):
    """ Product has clear error messaging when actions fail - handle common errors that occur when
      writing back to Nest devices, for example, locked thermostat, rate limit
    """
    if err.code == 401:
        """ Product handles revoked authorization by reverting to a disconnected state and removing all Nest user data
        - handle 401 unauthorized and how to refresh the app as well to enable a new oauth2 flow.
        """
        auth.remove_access()

    return jsonify(err.result)


if __name__ == "__main__":
    app.run(host=host, port=port)
