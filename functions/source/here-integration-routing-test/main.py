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

import cfnresponse
import traceback
import os
from botocore.vendored import requests


def handler(event, context):
  try:
    if event['RequestType'] == 'Create':
      # Test Credentials
      baseUrl = "https://route.api.here.com/routing/7.2"
      appId = os.environ["appId"]
      appCode = os.environ["appCode"]
      # prepare URLs
      url = '%s/calculateroute.json' % baseUrl
      parameters = {
        "app_id": appId,
        "app_code": appCode,
        "mode": "fastest;car;traffic:enabled",
        "language": "en-us",
        "waypoint0": "52.5160,13.3779",
        "waypoint1": "52.5206,13.3862"
      }
      # request
      print "Running routing request in Berlin"
      response = requests.get(url, params=parameters)
      print "Status code: " + str(response.status_code)
      if response.status_code != 200:
        raise Exception('Error: Status code received is not 200')
    elif event['RequestType'] == 'Update':
      pass
    elif event['RequestType'] == 'Delete':
      pass
    cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, '')
  except:
    print traceback.print_exc()
    cfnresponse.send(event, context, cfnresponse.FAILED, {}, '')