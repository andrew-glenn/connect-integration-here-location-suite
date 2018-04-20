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

# routing-query.py
# HERE Routing API lambda handler for Amazon Connect

import os
from botocore.vendored import requests


def lambda_handler(event, context):
  # unpack parameters
  details = event["Details"]
  parameters = details["Parameters"]
  positionFrom = parameters["positionFrom"].split(";")
  latFrom, lngFrom = float(positionFrom[0]), float(positionFrom[1])
  positionTo = parameters["positionTo"].split(";")
  latTo, lngTo = float(positionTo[0]), float(positionTo[1])
  waypoints = ((latFrom, lngFrom), (latTo, lngTo))

  route = getRoute(waypoints)
  if route is None: return None
  # send back ETA in minutes
  trafficTimeMinutes = int(route["trafficTime"] / 60.0)
  return {"TrafficTime": str(trafficTimeMinutes), "Status": "OK"}


def getRoute(waypoints):
  baseUrl = "https://route.api.here.com/routing/7.2"
  appId = os.environ["appId"]
  appCode = os.environ["appCode"]
  # prepare URLs
  url = '%s/calculateroute.json' % baseUrl
  parameters = {
    "app_id": appId,
    "app_code": appCode,
    "mode": "fastest;car;traffic:enabled",
    "language": "en-us"
  }
  for index, w in enumerate(waypoints):
    parameters["waypoint%d" % index] = 'geo!%f,%f' % (w[0], w[1])
  # queue
  response = requests.get(url, params=parameters)
  # process response
  json = response.json()
  if "response" not in json:
    return None
  route = json["response"]["route"][0]
  return route["summary"]
