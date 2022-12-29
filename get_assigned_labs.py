import sys
import os
import requests
import argparse
import json

#
# This retrieves all labs that are assigned in live campaigns, including labs for assignments that haven't started yet
#

auth_str = ""
user_agent_str = "SecLabs Python script"
invalid_creds_str = "ApiCredential missing"

def get_all_labs():

    baseurl = "https://securitylabs.veracode.com/api/lessons?limit=50&page=%s"
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}
      
    final_json = '{ "lessons": ['
    all_labs = []
    page_count = 0

    while True:

        # Sanity check
        if page_count>=100:
            print("We made 100 API calls! Stopping because that's unexpected.")
            break    
        
        # Set the page # in the URL string and do the Get Lessons API call
        url = baseurl % str(page_count)
        try:
            response = requests.get(url, headers=hdrs)
            if invalid_creds_str in response.text:
                print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
                return             
        except requests.RequestException as e:
            print("Exception calling the API! page_count is " + page_count)
            print(e)
            sys.exit(1)

        jsonObj = json.loads(response.text)
        these_labs = jsonObj["lessons"]

        for data in these_labs:
            all_labs.append(json.dumps(data))

        # nextPage will be null when no more data
        next =  jsonObj["nextPage"]
        if next is None:
            break

        page_count += 1

    # print("Total number of labs is " + str(len(all_labs)))
    for i, data in enumerate(all_labs):
        final_json = final_json + str(data)
        if i != len(all_labs) - 1: 
            final_json = final_json + ","
            
    final_json = final_json + "]}"
    print(final_json)

def main():
    
    parser = argparse.ArgumentParser(description="This script retrieves all labs that are assigned in live campaigns, including labs for assignments that haven't started yet. Output is in JSON format.")

    # Get auth string (key:secret) from environment variable
    try:
        global auth_str 
        auth_str = os.environ['SECLABS_API_AUTH']
    except KeyError as err:
        print(f"Required enironment variable not found! - {err}")
        sys.exit(1)

    get_all_labs()
 
if __name__=="__main__":
    main()  