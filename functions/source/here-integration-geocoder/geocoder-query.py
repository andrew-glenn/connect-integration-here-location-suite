# Copyright (C) 2018 HERE Europe B.V.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# geocoder-query.py
# HERE Geocoder API lambda handler for Amazon Connect

import os
from botocore.vendored import requests


def lambda_handler(event, context):
  # unpack parameters
  details = event["Details"]
  parameters = details["Parameters"]
  state = parameters["State"]
  city = parameters["City"]
  address = parameters["Address"]

  result = geocode(state, city, address)
  if result is None: return None
  lat, lng = result
  # send back in correct format
  position = "%s;%s" % (lat, lng)
  return {"position": position, "Status": "OK"}


def geocode(state, city, address):
  baseUrl = "https://geocoder.api.here.com/6.2"
  appId = os.environ["appId"]
  appCode = os.environ["appCode"]
  # prepare URLs
  url = baseUrl + "/geocode.json"
  parameters = {
    "app_id": appId,
    "app_code": appCode,
    "searchtext": "%s, %s, %s" % (address, city, state),
    "additionaldata": "AdditionalAddressProvider,25"}
  # request
  response = requests.get(url, params=parameters)
  # process response
  try:
    json = response.json()
  except Exception:
    print("no response, URL", response.url)
    return None
  result = json["Response"]["View"][0]["Result"][0]
  if result is None:
    print("no position, JSON", json)
    return None
  # unpack lat/lng
  position = result["Location"]["DisplayPosition"]
  if position is None:
    print("no position, RESULT", result)
    return None
  lat = float(position['Latitude'])
  lng = float(position['Longitude'])
  # return results
  return lat, lng
