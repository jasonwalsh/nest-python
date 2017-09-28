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
import glob
import shutil
import os
from datetime import timedelta
from datetime import datetime as dt
import urllib2
from flask import session

from wwn import sim_snapshot_url
from wwn import nest_data as models

json_file_name = "nest.json"
hist_days_allowed = 10
img_fields = models.NestData.get_camera_img_field_list()


def get_device(device_type, device_id):
    devices = get_cached_data(device_type)
    return devices.get(device_id) if devices else None


def delete_user_session():
    session.clear()


def delete_user_data():
    # delete persistent user data
    cameras = session.get('cameras')
    thermostats = session.get('thermostats')

    if cameras:
        # delete any camera files saved
        for camera_id, camera in cameras.iteritems():
            remove_images(camera.get("device_id"))

    if thermostats:
        # deleting any thermosatat files saved
        for therm_id, thermostat in thermostats.iteritems():
            delete_device_files("thermostats", therm_id)

    delete_user_session()


def process_data_changes(nestData):
    """ Process data such as checking for differences and deleting cached data."""

    # Keep track of differences if needed for views (if change in structure or camera ID/names).
    diffs = []

    prev_metadata = get_cached_data("metadata")
    prev_structs = get_cached_data("structures")
    prev_cams = get_cached_data("cameras")
    prev_therms = get_cached_data("thermostats")

    curr_metadata = nestData.get_metadata()
    curr_structs = nestData.get_structures()
    curr_cams = nestData.get_cameras()
    curr_therms = nestData.get_thermostats()

    # If there is no previous metadata then there was no previously cached API data
    if not prev_metadata:
        diffs.append("data")  # prev data may not have been initialized yet

    # client_version will not show as updated until the user reauthorizes and gets a new access_token
    # This is not needed for this sample but can change if tracking client_version is needed
    if prev_metadata and prev_metadata != curr_metadata:
        diffs.append("metadata")  # can check 'client_version' and 'access_token':

    # Check if changes to structures
    if prev_structs != curr_structs:
        diffs.append("structures")

    """ 
    Devices:Thermostats/Protects/Cameras:
    Product removes all the cached data as soon as the user removed the device
      or the structure with device/s - refresh the app
    Product removes any images/GIF's after the camera was removed as well
      if the subscription was removed from that camera - refresh the app

      Check changes to "is_video_history_enabled" or other settings
      (some settings might not return as true if using Nest Simulator):
    """
    if curr_cams:
        for camera_id, camera in curr_cams.iteritems():
            if not models.NestData.camera_has_subscription(camera):
                # camera does not have subscription: remove any cached images.
                remove_images(camera_id)  # remove any images/GIF's if the subscription was removed
            else:
                # Cache camera images for sample app. Could also cache "last_event.animated_image_url"
                # camera has subscription: cache images such as snapshot_url.
                cache_images(camera.get("device_id"), camera.get("snapshot_url"))

    if prev_cams:
        for camera_id, camera in prev_cams.iteritems():
            if not curr_cams or camera_id not in curr_cams:
                remove_images(camera_id)  # remove any images/GIF's after the camera was removed

    if prev_therms:
        for therm_id, thermostat in prev_therms.iteritems():
            if not curr_therms or therm_id not in curr_therms:
                delete_device_files("thermostats", therm_id)

    # find differences in camera values (excluding URLs or last_event) to see if some views should be refreshed
    if prev_cams and curr_cams and prev_cams != curr_cams:
        for camera_id, camera in curr_cams.iteritems():
            for key, value in camera.iteritems():
                if key not in img_fields:
                    prev_cam = prev_cams.get(camera_id)
                    if prev_cam is not None and prev_cam.get(key) != value:
                        diffs.append("cameras.{0}".format(key))

    # cache data for comparison (to skip rendering the template again, or check user data should be updated/removed
    cache_data(nestData)

    # delete history older than 10 days (checking with each request)
    delete_history()

    return diffs


def cache_data(nestData):
    # Use server session or db if size limit reached then cookie gets deleted
    if session is not None:
        session["metadata"] = nestData.get_metadata()
        session["structures"] = nestData.get_structures()
        session["smoke_co_alarms"] = nestData.get_smoke_co_alarms()
        session["cameras"] = nestData.get_cameras()
        session["thermostats"] = thermostats = nestData.get_thermostats()

        if thermostats:
            for thermostat_id, thermostat in thermostats.iteritems():
                # store json for each thermostat to retrieve thermostat history view
                store_json(thermostat, "thermostats", thermostat_id)

    store_json(nestData.get_data(), "data", json_file_name) # save JSON for troubleshooting if needed


def get_cached_data(key):
    if session is not None and key in session:
        return session[key]
    return ""


def cache_images(camera_id, image_url):
    if not image_url or image_url == sim_snapshot_url:
        return False

    if session is not None:
        prev_image_url = session.get("curr_" + camera_id) if camera_id else None
        if prev_image_url and prev_image_url != image_url:
            session[camera_id] = prev_image_url
        session["curr_" + camera_id] = image_url  # store URL or download image and store file URL
    try:
        image = download_image(image_url)

        date_dir = dt.strftime(dt.now(), '%Y-%m-%d')
        image_file = os.path.join("static", "users", date_dir, "cameras", '{0}.jpg'.format(camera_id))
        ensure_dir(image_file)
        with open(image_file, 'w') as f:
            f.write(image)

    except Exception as ex:
        print "Error trying to download file for ", camera_id, ": ", ex


def remove_images(camera_id):
    # remove_images
    try:
        if session and camera_id and camera_id in session:
            session[camera_id] = None
            print "cleared cached url for {0}: {1}".format(camera_id, session[camera_id])
        # delete image files
        delete_device_files("cameras", "{0}.jpg".format(camera_id))
    except Exception as ex:
        print "Error trying to delete file for ", camera_id, ": ", ex


def delete_history(days=hist_days_allowed):
    """
    Devices:Thermostats/Protects/Cameras:
    Product removes all the cached data as soon as the user removed the device
    or the structure with device/s - refresh the app

    Delete subfolders that have a directory name (could use create date instead)
    that is older than specified such as 10 days.
    """
    parent_dir = os.path.join("static", "users")
    curr_date = dt.now()
    old_date = curr_date - timedelta(days)
    curr_date_str = dt.strftime(curr_date, '%Y-%m-%d')
    old_date_str = dt.strftime(old_date, '%Y-%m-%d')
    print "delete folders older than: {0} ({1} days older than {2})".format(old_date_str, days, curr_date_str)
    entries = os.listdir(parent_dir)
    for entry in entries:
        if entry < old_date_str:
            entry_path = os.path.join(parent_dir, entry)
            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
            else:
                os.remove(entry_path)


def delete_device_files(device_type, device_id):
    """
     Devices:Thermostats/Protects/Cameras:
     Product removes all the cached data as soon as the user removed the device
       or the structure with device/s - refresh the app
    """
    parent_dir = os.path.join("static", "users")
    find_path = os.path.join(parent_dir, '*', device_type, device_id)
    device_files = glob.glob(find_path)
    for file_path in device_files:
        os.remove(file_path)


def get_device_files(device_type, device_id):
    hist_files = {}
    parent_dir = os.path.join("static", "users")
    find_path = os.path.join(parent_dir, '*', device_type, device_id)
    device_files = glob.glob(find_path)
    for file_name in device_files:
        paths = file_name.split('/')
        date_path = paths[2] if len(paths) > 2 else '00/00/00'
        try:
            with open(file_name, 'r') as f:
                json_content = json.loads(f.read())
        except IOError:
            json_content = ""
            # hist_files[date_path] = file
        hist_files[date_path] = json_content
    return hist_files


def get_device_file_paths(device_type, device_id):
    hist_files = {}
    parent_dir = os.path.join("static", "users")
    find_path = os.path.join(parent_dir, '*', device_type, device_id)
    device_files = glob.glob(find_path)
    for file_name in device_files:
        paths = file_name.split('/')
        date_path = paths[2] if len(paths) > 2 else '00/00/00'
        hist_files[date_path] = file_name
    return hist_files


def download_image(url):
    # Downloads the image from the specified URL to the filesystem
    if url is None or url == sim_snapshot_url:
        return None
    response = urllib2.urlopen(url)
    image = response.read()
    if image == '':
        raise IOError('The Snapshot URL did not contain any HTTP body when fetched')

    return image


def store_json(data=None, api_level="other", file_name=json_file_name):
    date_dir = dt.strftime(dt.now(), '%Y-%m-%d')
    file_path = os.path.join("static", "users", date_dir, api_level, file_name)
    ensure_dir(file_path)
    with open(file_path, "w") as f:
        json.dump(data, f, sort_keys=True, indent=4)


def fetch_json(file_name=json_file_name):
    try:
        with open(file_name, 'r') as f:
            return json.loads(f.read())
    except IOError:
        return ""


def ensure_dir(file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

