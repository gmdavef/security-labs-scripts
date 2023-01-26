import sys
import os
import requests
import argparse
import json

#
# This script adds a role to one or more users. 
#

auth_str = ""
user_agent_str = "SecLabs Python script"
invalid_creds_str = "ApiCredential"

def add_role(role, user_list):

    # Find the role ID for the given role name
    role_id = lookup_role_id(role)
    if role_id is None:
        return 0
    
    print("Role ID to be added is: " + role_id)

    # Loop on each user and update the roles 
    num_added = 0
    for u in user_list:

        # Find this user's ID and current role IDs
        user_id, role_ids = lookup_user_id_and_roles(u)

        if (user_id is not None):
    
            # Check if user already has this role. If so we can skip the rest.
            if role_id in role_ids:
                print("Skipping...user already has role")
            else:
                # Append the role ID to the current list
                role_ids.append(role_id)

                # Build the JSON request body and do the Put User API call
                req_body = { "roleIds": role_ids }
                url = "https://securitylabs.veracode.com/api/users/" + user_id
                hdrs = {"User-Agent": user_agent_str, "auth": auth_str}
                try:
                    print("Updating user's roles...")
                    response = requests.put(url, headers=hdrs, json=req_body)
                    code = response.status_code
                    # print("response code is: " + str(code))                 
                    if code == 200:
                        num_added += 1
                except requests.RequestException as e:
                    print("Exception calling the Put Users API!")
                    print(e)

    return num_added


def lookup_user_id_and_roles(user):

    print(">>> Looking up ID and roles for: " + user)
    if (len(user) <=2):
        print("At least 3 characters must be provided for each user. Skipping.")
        return None, []

    url = "https://securitylabs.veracode.com/api/users/details?phrase=" + user
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}

    # Do the Get Users Details API call
    try:
        response = requests.get(url, headers=hdrs)
        if invalid_creds_str in response.text:
            print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
            return        
    except requests.RequestException as e:
        print("Exception calling Get Users Details API!")
        print(e)
        sys.exit(1)

    thisdict = json.loads(response.text)
    users = thisdict["users"]

    # Make sure we got exactly one user
    if len(users) == 0:
        print("Unable to find that user. Or user may be disabled. Skipping.")
        return None, []
    elif len(users) > 1:
        print("More than one user matched. Skipping.")
        return None, []
    
    # Grab the user ID
    userobj = users[0]
    userid = userobj.get("id")
    print("User ID is " + userid)
   
    # Grab each of the each role IDs
    roleobjs = userobj.get("roles")
    print("Current # of roles is " + str(len(roleobjs)))
    roleids = []
    for r in roleobjs:
        id = r["id"]
        roleids.append(id)
   
    return userid, roleids


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
        # print("name=" + name + ", id=" + id)
        if name == role:
            return id
    
    print("Can't find that role. Make sure it exists and uppercase/lowercase is correct.")
    return

def load_users_from_file(filename):

    # Note that File must contain names (not emails). This is due to BUG LRN-4411.
    try:
        file1 = open(filename, "r")
        users = file1.readlines()
        users2 = [i.strip() for i in users]
        print("Read {} users from the file.".format(len(users2)))
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

    parser = argparse.ArgumentParser(description="This script adds the given role to the user(s) provided. Existing roles are retained.")
    parser.add_argument("--role", required=True, help="Name of Security Labs role to be added.")
    parser.add_argument("--user", required=False, help="Target user's name within Security Labs. Use only if adding role to a single user.")
    parser.add_argument("--file", required=False, help="Text file containing names of target users in a single column. Use when adding role to multiple users.")
    
    args = parser.parse_args()

    # Check that --user or --file was provided
    if ("--user" not in sys.argv) and ("--file" not in sys.argv):
        print("Error: You must provide either --user or --file.")
        return   

    # Check that both options weren't provided
    if ("--user" in sys.argv) and ("--file" in sys.argv):
        print("Error: --user and --file are mutually exclusive.")
        return   

    # Get auth string (key:secret) from environment variable
    try:
        global auth_str 
        auth_str = os.environ["SECLABS_API_AUTH"]
    except KeyError as err:
        print(f"Error: Required environment variable not found - {err}")
        return

    # Create the list of users to update
    role = args.role.strip()
    theuser = args.user.strip() if args.user is not None else None
    filename = args.file.strip() if args.file is not None else None
    user_list = [ theuser ] if theuser is not None else load_users_from_file(filename.strip())

    # Add role to the user(s)
    count = 0
    if len(user_list) > 0:
        count = add_role(role, user_list)

    if count > 0:
        print("Done! Added role to {} users.".format(count))
    else:
        print("No users updated.")    


if __name__=="__main__":
    main()  