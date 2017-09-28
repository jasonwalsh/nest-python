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

from flask import render_template
from collections import OrderedDict
import json

import data_store
from wwn import sim_snapshot_url


def get_api_content(request, nestData, diff_list):
    """ Returns HTML generated from Jinja2 templates.  Uses current data 
    to show all available structures and devices, and present a schedule view
    to update some properties.
    """
    has_prev_content = "poller_id" in request.args
    template_args = {
        "data": nestData,
        "msgmap": get_locale_msgs(nestData),
        "expanded_ids": request.cookies.get("expandedIds", []),
        "sim_snapshot_url": sim_snapshot_url
    }

    # Generate schedule menu HTML if there are changes to the data needed for those menus
    if has_prev_content and (diff_list is None or len(diff_list) == 0):
        print "No change in top-level API data needed for schedule view"
        sched_html = None
    else:
        sched_html = render_template("nestdata_schedule.html", **template_args)

    # Generate API data HTML on each request to show structures and any devices such as thermostats.
    content_html = render_template("nestdata.html", **template_args)

    return {"content": content_html, "schedule": sched_html}


def get_camera_imgs(camera_id, camera):
    """ Returns HTML generated from Jinja2 templates.  Looks for saved camera files to 
    to show in history view.
    """
    hist_files = data_store.get_device_file_paths('cameras', '{0}.jpg'.format(camera_id))

    ordered = OrderedDict(reversed(sorted(hist_files.items(), key=lambda item: item[0])))

    template_args = {
        "device": camera,
        "image_files": ordered,
        "sim_snapshot_url": sim_snapshot_url
    }

    content = render_template('nestcam_imgs.html', **template_args)

    return {"device_content": content}


def get_thermostat_hist(thermostat_id, thermostat):
    """ Returns HTML generated from Jinja2 templates.  Looks for saved thermostat data to 
    to show in history view.
    """
    hist_files = data_store.get_device_files('thermostats', thermostat_id)

    ordered = OrderedDict(reversed(sorted(hist_files.items(), key=lambda item: item[0])))

    template_args = {
        "device": thermostat,
        "hist_files": ordered
    }

    content = render_template('thermostat_hist.html', **template_args)

    return {"device_content": content}


def get_locale_msgs(nestData):
    """ Get locale from last thermostat and read the message/label file for that localization
        Will not be able to get locale without a thermostat. Uses default config.json if no thermostat or 
        file is not found for that locale. This is just used for excluding properties not listed as labels, 
        and for icons next to device names. Could get locale from user agent instead of from API data.
    """
    msgs = None
    locale = nestData.get_locale()
    print "locale = ", locale
    try:
        if locale:
            with open('config_' + locale + '.json') as jsonfile:
                msgs = json.loads(jsonfile.read())
    except Exception as ex:
        print "Error trying to open configuration file for locale: ", locale, ex

    if not msgs:
        try:
            with open('config.json') as jsonfile:
                msgs = json.loads(jsonfile.read())
        except Exception as ex1:
            print "Error trying to open config.json: ", ex1

    if not msgs:
        msgs = {}
    if "labels" not in msgs:
        msgs["labels"] = {}
    if "fa-icons" not in msgs:
        msgs["fa-icons"] = {}
    return msgs


def convert_form(request):
    # replace 'true' and 'false' with True and False, other conversions as needed
    data = ""
    form_fields = request.form if request and request.form else None
    if form_fields:
        conv_form_fields = {}
        for fld, val in form_fields.iteritems():
            conv_form_fields[fld] = True if val == 'true' else False if val == 'false' else val
        data = json.dumps(conv_form_fields)

    return data

