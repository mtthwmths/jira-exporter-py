import urllib.request
from urllib.error import HTTPError, URLError
import json
import html
import csv, sys

filename = 'some.csv'
url = "<root-url>/jira/rest/api/latest/search"
jql = "project = PROJKEY ORDER BY key DESC"
maxResults = 100
data = {
    "jql":html.escape(jql, quote=True),
    "maxResults":maxResults
}
url_values = urllib.parse.urlencode(data)
# this url is public, and if you have a wrong token
# response.getheaders() will show X-AUSERNAME as 'anonymous'
# but for a good token
# response.getheaders() will show X-AUSERNAME as the username associated with the PAT
# NOTE: if this were an admin endpoint, and there was a bad token
# response.code would return 403 because 'anonymous' user cannot access admin functions
auth_token = "<your-token-here>"

# Create a request object with the URL and headers
req = urllib.request.Request(url+'?'+url_values)
req.add_header("Authorization", f"Bearer {auth_token}")
 
try:
    response = urllib.request.urlopen(req)
    response_results = response.read().decode("utf-8")
    results_json = json.loads(response_results)
    results_dict = {x.get('key'): x for x in results_json['issues']}
    total = results_json['total']
    startAt = maxResults
    data['startAt'] = startAt
    while(startAt < total):
        url_values = urllib.parse.urlencode(data)
        req = urllib.request.Request(url+'?'+url_values)
        req.add_header("Authorization", f"Bearer {auth_token}")
        response = urllib.request.urlopen(req)
        response_results = response.read().decode("utf-8")
        results_json = json.loads(response_results)
        results_dict.update({x.get('key'): x for x in results_json['issues']})
        startAt = startAt + maxResults
        data['startAt'] = startAt
    # Process the JSON data or perform any other operations
    # print(results_dict.get('PROJKEY'))
# HTTPError has to come first or URLError would catch 400-599 errors
except HTTPError as e:
    print('The server couldn\'t fulfill the request. Error code: ', e.code)
except URLError as e:
    print("Error: Failed to make the request. Reason:", e.reason)
except json.JSONDecodeError as e:
    print("Error: Failed to decode JSON response. Reason:", e)
else:
    print(f"found {total} issues")

with open('some.csv', 'w', newline='') as f:
    try:
        # make a csv out of results_dict
        fieldnames = []
        breakpoint()
        for k,v in results_dict.items():
            fields = list(v['fields'].keys())
            fieldnames = list(set(fieldnames + fields))
        fieldnames.sort()
    # make a dictWriter
    except csv.Error as e:
        sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))
