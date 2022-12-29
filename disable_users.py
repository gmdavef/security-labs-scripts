import sys
import os
import requests
import argparse
import json

#
# This script diables one or more users. 
#

auth_str = ""
user_agent_str = "SecLabs Python script"
invalid_creds_str = "ApiCredential missing"

def disable_user(user_list):

    # Loop on each user to update them 
    num_updated = 0
    for u in user_list:

        # Find this user's ID and current role IDs
        user_id = lookup_user_id(u)

        if (user_id is not None):
    
            # Build the JSON request body and do the Put User API call
            req_body = { "disabled": "true" }
            url = "https://securitylabs.veracode.com/api/users/" + user_id
            hdrs = {"User-Agent": user_agent_str, "auth": auth_str}
            try:
                print("Updating user...")
                response = requests.put(url, headers=hdrs, json=req_body)
                code = response.status_code
                print("response code is: " + str(code))                 
                if code == 200:
                    num_updated += 1
            except requests.RequestException as e:
                print("Exception calling the Put Users API!")
                print(e)

    return num_updated


def lookup_user_id(user):

    print(">>> Looking up ID for: " + user)
    if (len(user) <=2):
        print("At least 3 characters must be provided for each user. Skipping.")
        return None

    url = "https://securitylabs.veracode.com/api/users/details?phrase=" + user
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}

    # Do the Get Users Details API call
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
    users = thisdict["users"]

    # Make sure we got exactly one user
    if len(users) == 0:
        print("Unable to find that user. Or user may already be disabled. Skipping.")
        return None
    elif len(users) > 1:
        print("More than one user matched. Skipping.")
        return None
    
    # Grab the user ID
    userobj = users[0]
    userid = userobj.get("id")
    print("User ID is " + userid)
    return userid


def load_users_from_file(filename):

    try:
        file1 = open(filename, "r")
        users = file1.readlines()
        users2 = [i.strip() for i in users]
        print("users read from file are: " + str(users2))
        file1.close()
    except FileNotFoundError as e:
        print(e)
        print("That file doesn't seem to exist. Please try again.")        
        return []
    except UnicodeDecodeError as e:
        print(e)
        print("File has some unexpected characters. Please make sure it's a text file and try again.")
        return []

    return users2


def main():

    parser = argparse.ArgumentParser(description="This script disables the user(s) provided.")
    parser.add_argument("--user", required=False, help="User's full name or email address.")
    parser.add_argument("--user_file", required=False, help="Text file with list of user names or email addresses in a single column.")
    
    args = parser.parse_args()

    # Ensure that either --user or --user_file was provided
    if ("--user" not in sys.argv) and ("--user_file" not in sys.argv):
        print("Error: You must provide either --user or --user_file.")
        return
        
    # Ensure that both options weren't provided
    if ("--user" in sys.argv) and ("--user_file" in sys.argv):
        print("Error: --user and --user_file are mutually exclusive.")
        return              

    # Get auth string (key:secret) from environment variable
    try:
        global auth_str 
        auth_str = os.environ["SECLABS_API_AUTH"]
    except KeyError as err:
        print(f"Error: Required enironment variable not found - {err}")
        return
    
    # Create the list of users to disable    
    theuser = args.user.strip() if args.user is not None else None
    filename = args.user_file.strip() if args.user_file is not None else None
    user_list = [ theuser ] if theuser is not None else load_users_from_file(filename.strip())
   
    # Disable the user(s)
    count = 0
    if len(user_list) > 0:    
        count = disable_user(user_list)

    if count > 0:
        print("Done! Disabled {} users.".format(count))
    else:
        print("No users were disabled.")    
 
if __name__=="__main__":
    main()  