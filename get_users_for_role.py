import sys
import os
import requests
import argparse
import json

#
# This script returns all users with the given role. 
#

auth_str = ""
user_agent_str = "SecLabs Python script"
invalid_creds_str = "ApiCredential missing"

def get_users(role, output_format):

    final_json = '{ "users": ['
    all_users = []
    page_count = 0

    # Find the role ID for the given role name
    role_id = lookup_role_id(role)
    if role_id is None:
        return 0
    
    # Invoke Get Users Details with roleIds parameter. Max is 50 users at a time.  
    # TODO: add code to handle pagination
    baseurl = "https://securitylabs.veracode.com/api/users/details?limit=50&page=%s&roleIds=" + role_id
    url = baseurl % str(page_count)
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}
    try:
        response = requests.get(url, headers=hdrs)
        if invalid_creds_str in response.text:
            print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
            return None     
    except requests.RequestException as e:
        print("Exception calling Get Users Details API!")
        print(e)
        sys.exit(1)

    thisdict = json.loads(response.text)
    these_users = thisdict["users"]

    for user in these_users:
        # Remove superfluous data elements, keep the 3 we need
        uid = user["id"]
        uemail = user["email"]
        uname = user["name"]
        user.clear()
        user.update({"id": uid})
        user.update({"email": uemail})
        user.update({"name": uname})
        all_users.append(json.dumps(user))

    # Add this set of users to the overall list
    # print("Total number of users is " + str(len(all_users)))
    for i, data in enumerate(all_users):
        final_json = final_json + str(data)
        if i != len(all_users) - 1: 
            final_json = final_json + ","
            
    final_json = final_json + "]}"
    send_output(final_json, output_format)

    return len(all_users)


def send_output(json_str, format):

    if (format == "JSON"):
        print(json_str)
    elif (format == "CSV"):
        # output to 3 column csv format - NAME, EMAIL, ID
        thisdict = json.loads(json_str)
        these_users = thisdict["users"]
        for user in these_users:
            print(user["name"], user["email"], user["id"], sep=", ")
            

def lookup_role_id(role):

    # Do the Get Roles API call
    url = "https://securitylabs.veracode.com/api/roles"
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}
    try:
        response = requests.get(url, headers=hdrs)
        if invalid_creds_str in response.text:
            print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
            return
    except requests.RequestException as e:
        print("Exception calling Get Roles API!")
        print(e)
        sys.exit(1)

    thisdict = json.loads(response.text)

    # Loop on each returned role to find a match
    for r in thisdict:
        id = r["id"]
        name = r["name"]
        if name == role:
            return id
    
    print("Can't find that role. Make sure it exists and uppercase/lowercase is correct.")
    return


def main():
    
    parser = argparse.ArgumentParser(description="This script returns the list of users for a given role.")
    parser.add_argument("--role", required=True, help="Name of Security Labs role")
    parser.add_argument("--format", required=False, help="Output format. Valid values are JSON (default), CSV", default="JSON")
    
    args = parser.parse_args()
    role = args.role.strip()

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

    # Retrieve the users for the role
    count = get_users(role, format)
   
 
if __name__=="__main__":
    main() 