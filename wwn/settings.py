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

import os

# OAuth2 client ID and secret copied from https://console.developers.nest.com/products/(selected product)
# Keep product ID and product secret private (don't store this in a public location).
product_id     = os.environ.get("PRODUCT_ID", None)
product_secret = os.environ.get("PRODUCT_SECRET", None)

# Port number for sample application and callback URI (must be the same port)
port = 5000  

# OAuth2 URLs
nest_auth_url =         'https://home.nest.com/login/oauth2'
nest_access_token_url = 'https://api.home.nest.com/oauth2/access_token'
nest_api_root_url     = 'https://api.home.nest.com'
nest_tokens_path      = '/oauth2/access_tokens/'

# API URL after authorization
nest_api_url          = 'https://developer-api.nest.com'

# URL to exclude (if camera has this snapshot URL then getting 404 not found errors tyring to download)
sim_snapshot_url = 'https://developer.nest.com/simulator/api/v1/nest/devices/camera/snapshot'
