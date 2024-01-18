"""
rest_jira_exporter.py should allow someone with access to a jira projects issues
to export them using the rest API to avoid frontend limitation using things like
bulk edit or the csv export in issue search.
"""
import urllib.request
from urllib.error import HTTPError, URLError
import json
import html
import csv
import sys

def main():
    """
    main function for rest_jira_exporter
    """
    filename = "some.csv"
    rool_url = "<your-root-url>"
    project_key = "SD"
    auth_token = "<your-token-here>"
    max_results = 100

    url = f"{rool_url}/jira/rest/api/latest/search"
    # this url is public, and if you have a wrong token
    # response.getheaders() will show X-AUSERNAME as 'anonymous'
    # but for a good token
    # response.getheaders() will show X-AUSERNAME as the username associated with the PAT
    # NOTE: if this were an admin endpoint, and there was a bad token
    # response.code would return 403 because 'anonymous' user cannot access admin functions
    jql = f"project = {project_key} ORDER BY key DESC"

    data = {
        "jql":html.escape(jql, quote=True),
        "maxResults":max_results
    }
    url_values = urllib.parse.urlencode(data)

    # Create a request object with the url and headers
    req = urllib.request.Request(url+'?'+url_values)
    req.add_header("Authorization", f"Bearer {auth_token}")

    try:
        response = urllib.request.urlopen(req)
        response_results = response.read().decode("utf-8")
        results_json = json.loads(response_results)
        results_dict = {x.get('key'): x for x in results_json['issues']}
        total = results_json['total']
        start_at = max_results
        data['start_at'] = start_at
        while start_at < total:
            url_values = urllib.parse.urlencode(data)
            req = urllib.request.Request(url+'?'+url_values)
            req.add_header("Authorization", f"Bearer {auth_token}")
            response = urllib.request.urlopen(req)
            response_results = response.read().decode("utf-8")
            results_json = json.loads(response_results)
            results_dict.update({x.get('key'): x for x in results_json['issues']})
            start_at = start_at + max_results
            data['start_at'] = start_at
        # Process the JSON data or perform any other operations
        # print(results_dict.get('project_key'))
    # HTTPError has to come first or URLError would catch 400-599 errors
    except HTTPError as e:
        print('The server couldn\'t fulfill the request. Error code: ', e.code)
    except URLError as e:
        print("Error: Failed to make the request. Reason:", e.reason)
    except json.JSONDecodeError as e:
        print("Error: Failed to decode JSON response. Reason:", e)
    else:
        print(f"found {total} issues")

    with open(filename, "w", newline="", encoding="utf-8") as f:
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
            sys.exit(f"file {filename}, line {csv.reader.line_num}: {e}")

if __name__ == '__main__':
    main()
