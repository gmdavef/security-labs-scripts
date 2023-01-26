import sys
import os
import requests
import argparse
import json
import urllib.parse

#
# This script returns all labs relevant to a given keyword or phrase. 
#

auth_str = ""
user_agent_str = "SecLabs Python script"
invalid_creds_str = "ApiCredential"

def get_labs(keyword, output_format):

    page_count = 0
    all_labs = []
    final_json = '{ "labs": ['

    # Hard-code limit to 50, which is the max number allowed by the API.  
    encoded_keyword = urllib.parse.quote(keyword)
    baseurl = "https://securitylabs.veracode.com/api/lessons/search?limit=50&phrase=" + encoded_keyword
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}

    while True:

        if page_count>=50:
            print("We made 50 API calls! Stopping because that's much more than expected.")
            break

        # Set the page num in the URL string and do the Get Lessons by Topic API call.
        url = baseurl + "&page=" + str(page_count)
        try:
            response = requests.get(url, headers=hdrs)
            # Check for non-200 response
            code = response.status_code
            if code != 200:
                if invalid_creds_str in response.text:
                    print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
                    sys.exit(1)
                else:
                    print("Response code is: " + str(code))
                    print("Response body is: " + response.text)
                    sys.exit(1)

        except requests.RequestException as e:
            print("Exception calling Get Lessons By Topic API!")
            print(e)
            sys.exit(1)

        jsonObj = json.loads(response.text)
        these_labs = jsonObj["lessons"]

        if page_count==0 and len(these_labs)==0:
            return 0
        else:
            for data in these_labs:
                all_labs.append(json.dumps(data))

        # If this is the last page of data, nextUrl under pages will be null
        pagesObj =  jsonObj["pages"]
        if (pagesObj is None or pagesObj["nextUrl"] is None):
            break

        page_count += 1

    # Add all labs to the final json string
    for i, data in enumerate(all_labs):
        final_json = final_json + str(data)
        if i != len(all_labs) - 1: 
            final_json = final_json + ","

    final_json = final_json + "]}"
    send_output(final_json, output_format)

    return len(all_labs)


def send_output(json_str, format):

    thisdict = json.loads(json_str)
    these_labs = thisdict["labs"]

    if len(these_labs)>0:

        if (format == "JSON"):
            # output json string we already have
            print(json_str)
        elif (format == "CSV"):
            # output to 4 column CSV format, with a header row
            print("LAB NAME", "LAB TYPE", "LANGUAGE", "LAB URL", sep=", ")
            for lab in these_labs:
                # remove any commas from lab name 
                title_str = str(lab["title"]).replace(",", "")
                type_str = "challenge" if lab["challenge"]==True else "lesson"
                print(title_str, type_str, lab["stack"], lab["url"], sep=", ")
        

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
        print(f"Error: Required environment variable not found - {err}")
        return
    
    if len(keyword)<=1:
        print("Error: The keyword provided must be at least 2 characters")
        return

    format = "JSON"
    if ("--format" in sys.argv):
        format = args.format.upper()

    if (format not in ["JSON", "CSV"]):
        print("Error: --format must be JSON or CSV")
        return

    count = get_labs(keyword, format)
    if count==0:
        print("No labs found for '" + keyword + "'")
   
 
if __name__=="__main__":
    main() 