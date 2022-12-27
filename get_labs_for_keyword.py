import sys
import os
import requests
import argparse
import json
import urllib.parse

#
# This script returns all labs for a given keyword or phrase. 
#

auth_str = ""
user_agent_str = "SecLabs Python script"
invalid_creds_str = "ApiCredential missing"

def get_labs(keyword, output_format):

    final_json = '{ "labs": ['
    all_labs = []
    page_count = 0

    # Invoke Get Lessons By Topic with phrase parameter. Max is 50 labs at a time.  
    # TODO: add code to handle pagination
    print("Searching labs relevant to: " + keyword)
    encoded_keyword = urllib.parse.quote(keyword)
    baseurl = "https://securitylabs.veracode.com/api/lessons/search?limit=50&page=%s&phrase=" % str(page_count)
    url = baseurl + encoded_keyword
    # print("Invoking url: " + url)
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}

    try:
        response = requests.get(url, headers=hdrs)
        if invalid_creds_str in response.text:
            print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
            return None     
    except requests.RequestException as e:
        print("Exception calling Get Lessons By Topic API!")
        print(e)
        sys.exit(1)

    thisdict = json.loads(response.text)
    these_labs = thisdict["lessons"]

    for data in these_labs:
        all_labs.append(json.dumps(data))

    # Add this set of labs to the overall list
    
    print("Total number of labs is " + str(len(all_labs)))
    for i, data in enumerate(all_labs):
        final_json = final_json + str(data)
        if i != len(all_labs) - 1: 
            final_json = final_json + ","
            
    final_json = final_json + "]}"

    send_output(final_json, output_format)

    return len(all_labs)


def send_output(json_str, format):

    if (format == "JSON"):
        print(json_str)
    elif (format == "CSV"):
        # TODO: output to a tabular CSV format (lab name, lesson | challenge, language, url of lab)
        print("csv output will be here")
        

def main():
    
    parser = argparse.ArgumentParser(description="This script returns a list of relevant labs for the given keyword or phrase.")
    parser.add_argument("--keyword", required=True, help="Keyword or phrase to search on")
    parser.add_argument("--format", required=False, help="Output format. Valid values are JSON (default), CSV", default="JSON")
    
    args = parser.parse_args()
    keyword = args.keyword.strip()

    # Get auth string (key:secret) from environment variable
    try:
        global auth_str 
        auth_str = os.environ["SECLABS_API_AUTH"]
    except KeyError as err:
        print(f"Error: Required enironment variable not found - {err}")
        return
    
    format = "JSON"
    if ("--format" in sys.argv):
        format = args.format

    if (format not in ["JSON", "CSV"]):
        print("Error: --format must be JSON or CSV")
        return

    count = get_labs(keyword, format)

    print("Found {} labs for that keyword.".format(count))
   
 
if __name__=="__main__":
    main() 