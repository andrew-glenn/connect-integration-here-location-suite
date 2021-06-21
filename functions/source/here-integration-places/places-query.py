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

# places-query.py
# HERE Places API lambda handler for Amazon Connect

import os
from botocore.vendored import requests


def lambda_handler(event, context):
  # unpack parameters
  details = event["Details"]
  parameters = details["Parameters"]
  position = parameters["position"].split(";")
  lat, lng = float(position[0]), float(position[1])
  radius = float(parameters["radius"])
  category = parameters["Category"] if "Category" in parameters else None
  
  places = getPlaces(lat, lng, radius, category)
  if places is None: return None
  count = len(places)
  if count == 0: return None
  first = places[0]
  nameFirst, latFirst, lngFirst = first["name"], first["lat"], first["lng"]
  # send back Places API response
  positionFirst = "%s;%s" % (latFirst, lngFirst)
  return {"positionFirst": positionFirst, "NameFirst": nameFirst, "Count": str(count), "Status": "OK"}


def getPlaces(lat, lng, radius, category):
  # get configuration
  baseUrl = "https://places.api.here.com/places/v1"
  appId = os.environ["appId"]
  appCode = os.environ["appCode"]
  # build request
  url = '%s/discover/explore' % baseUrl
  parameters = {
    "app_id": appId,
    "app_code": appCode,
    "at": "{0},{1};u={2}".format(lat, lng, radius),
    "cat": "" if category is None else category
  }
  # call API synchronously
  response = requests.get(url, params=parameters)
  # process response
  try:
    json = response.json()
  except Exception:
    print(("no response", response.url))
    return None
  if "results" not in json:
    print(("invalid response", json))
    return None
  # extract places information
  places = json["results"]["items"]
  extractPlace = lambda p: {
    "placeId": p['id'],
    "lat": p["position"][0] if "position" in list(p.keys()) else None,
    "lng": p["position"][1] if "position" in list(p.keys()) else None,
    "distance": p["distance"] if "distance" in list(p.keys()) else None,
    "name": p["title"] if "title" in list(p.keys()) else None,
    "address": p["vicinity"] if "vicinity" in list(p.keys()) else None,
    "url": p["href"] if "href" in list(p.keys()) else None,
    "locationType": "display" if "position" in list(p.keys()) else None,
    "averageRating": p["averageRating"] if "averageRating" in list(p.keys()) else None,
    "categoryTitle": p["category"]["title"] if "category" in list(p.keys()) else None,
    "categoryId": p["category"]["id"] if "category" in list(p.keys()) else None
  }
  places = list(map(extractPlace, places))
  # return as list
  return list(places)
