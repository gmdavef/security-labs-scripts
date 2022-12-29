import sys
import os
import requests
import argparse
import json

#
# This script invites one or more people to join Security Labs.
#

auth_str = ""
user_agent_str = "SecLabs Python script"
invalid_creds_str = "ApiCredential missing"

def create_invitations(user_list, invited_by, send_email):

    sender_id = ""
    # Check if invited_by is an email address. If so, we need to error out due to BUG LRN-4411.
    if ("@" in invited_by) and ("." in invited_by):
        print("Sorry, invited_by must be a name or user ID. Email address does not work currently.")
        return 0

    # If invited_by is 24 chars and starts with a number, assume it's an ID.
    # Otherwise assume it's a name and we need to make an API call to get the ID.
    if (len(invited_by)==24) and (invited_by[0].isdigit()):
        sender_id = invited_by    
    else:
        sender_id = lookup_user_id(invited_by)
        if (sender_id is None):
            return 0

    # Loop on each user and create the invitation 
    num_invited = 0
    for user in user_list:

        u = user["user"]
        email_addr = u[0]
        name = u[1]
        
        # The API currently invites a user even if they already exist. BUG LRN-4425 was opened for this.
        # If BUG LRN-4411 were fixed, we could do the check ourselves with below code. For now, must live with this limitation.
        # if ( user_exists(email_addr) ):
        #    print("Existing user found with that email. Skipping.")
        #    continue  
        
        # Build the JSON request body and do the Post Invite API call
        req_body = { "email": email_addr, "name": name, "senderId": sender_id, "sendEmail": send_email }    
        req_body_json = json.dumps(req_body)

        url = "https://securitylabs.veracode.com/api/invites"
        hdrs = {"User-Agent": user_agent_str, "Content-Type": "application/json", "auth": auth_str}
        try:
            print(">>>Inviting user: " + email_addr)
            response = requests.post(url, headers=hdrs, json=req_body)
            if invalid_creds_str in response.text:
                print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
                sys.exit(1)  
            
            code = response.status_code
            if code == 200:
                print("Resp code is 200. User invited.")
                num_invited += 1
            elif code == 500:
                # Need this because the API currently returns 500 with message "unknown error" when invite is successfully created.
                # BUG LRN-4424 was opened for this.
                if "unknown error" in response.text:
                    print("Resp code is 500, but user invited.")
                    num_invited += 1                
            elif code == 400:
                # Check body for "Sender ID is invalid" or "Email is invalid"
                if "Sender id" in response.text:
                    print("Sender ID is invalid. Please check it and try again.")   
                elif "Email is invalid" in response.text:
                    print("Email for this user is wrong format. Skipping.")                                           
            elif code == 403:
                # Check body for "Invite already exists" 
                if "already exists" in response.text:
                    print("Invitation for this user already exists. Skipping.")       

        except requests.RequestException as e:
            print("Exception calling the Invite Users API!")
            print(e)

    return num_invited


def user_exists(email):

    url = "https://securitylabs.veracode.com/api/users/details?phrase=" + email
    hdrs = {"User-Agent": user_agent_str, "auth": auth_str}

    # Do the Get Users Details API call
    try:
        print("Invoking " + url)
        response = requests.get(url, headers=hdrs)
        if invalid_creds_str in response.text:
            print("Invalid API credentials. Check your SECLABS_API_AUTH environment variable.")
            sys.exit(1)     
    except requests.RequestException as e:
        print("Exception calling Get Users Details API!")
        print(e)
        sys.exit(1)

    thisdict = json.loads(response.text)
    users = thisdict["users"]

    if len(users) >= 1:
        return True
    
    return False


def load_users_from_file(filename):

    myuserlist = []
    try:
        file1 = open(filename, "r")
        lines = file1.readlines()
        for line in lines:
            str_list = line.split(",")
            if len(str_list) == 1:
                # only email present
                email_and_name = [ str_list[0].strip(), "" ]
            elif len(str_list) >= 2:
                # both email and name present
                email_and_name = [ str_list[0].strip(), str_list[1].strip() ]               
            list1 = { "user": email_and_name }
            myuserlist.append(list1)
        # print("Users parsed from file: " + str(myuserlist))
        file1.close()
    except FileNotFoundError as e:
        print(e)
        print("That file doesn't seem to exist. Please try again.")        
        return []
    except UnicodeDecodeError as e:
        print(e)
        print("File has some unexpected characters. Please make sure it's a text file and try again.")
        return []

    return myuserlist


def lookup_user_id(user):

    print(">>> Looking up ID for: " + user)
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
        print("Unable to find that user. Stopping.")
        return None
    elif len(users) > 1:
        print("More than one user matched. Stopping.")
        return None
    
    # Grab the user ID
    userobj = users[0]
    userid = userobj.get("id")
    print("Got User ID of " + userid)
    return userid


def main():

    parser = argparse.ArgumentParser(description="This script invites people to join Security Labs. Invited users are automatically assigned the default role(s).")
    parser.add_argument("--file", required=True, help="Name of CSV file with list of people to invite (email, name) in two columns. Email is required. Name is optional.")
    parser.add_argument("--invited_by", required=True, help="Name, Email, or ID of admin user that is creating the invitation(s). NOTE: Email doesn't work currently due to a bug in the API.")    
    parser.add_argument("--send_email", required=False, help="Whether to send invitation email. Valid values are true or false. The default is true.", default="true")

    args = parser.parse_args()
    invited_by = args.invited_by.strip() if args.invited_by is not None else None    
    send_email_str = args.send_email.strip() if args.send_email is not None else None
    send_email = True if send_email_str.lower() == "true" else False 

    # Create the list of users to invite
    filename = args.file.strip() if args.file is not None else None
    user_list = load_users_from_file(filename.strip())

    # Get auth string (key:secret) from environment variable
    try:
        global auth_str 
        auth_str = os.environ["SECLABS_API_AUTH"]
    except KeyError as err:
        print(f"Error: Required enironment variable not found - {err}")
        return

    # Invite the user(s)
    count = 0
    if len(user_list) > 0:
        print("Creating invitations now...")
        count = create_invitations(user_list, invited_by, send_email)

    if count > 0:
        print("Done! Created invite for {} users.".format(count))
    else:
        print("No users invited.")    


if __name__=="__main__":
    main()  