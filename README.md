# Security Labs Scripts #
Python scripts to automate various administrative tasks in Veracode Security Labs.

NOTE: These scripts require a local environment variable called **SECLABS_API_AUTH** with a value of {key}:{secret}, where {key} and {secret} are the API credentials generated by a Security Labs administrator from the Team Settings page in the UI.

## add_role_to_users.py ##
This script adds the given role to the user(s) provided. Existing roles are retained.

**Usage**

`add_role_to_users.py [-h] --role ROLE [--user USER] [--file FILE]`

* `--role` the role name to be added (exact case required)
* `--user` target user's name; use to add role to a single user
* `--file` a text file containing names of the target users in a single column; use when adding role to multiple users 

NOTE: `--user` and `--file` are mutually exclusive 

**Examples**
```
> python add_role_to_users.py --role "New Hires" --file users.txt

> python add_role_to_users.py --role "Mobile App Developer" --user "John Smith"
```

## disable_users.py ##
This script disables the user(s) provided.

**Usage**

`disable_users.py [-h] [--user USER] [--file FILE]`

* `--user` target user's name; use to disable a single user
* `--file` a text file containing names of the target users in a single column; use when disabling multiple users

NOTE: `--user` and `--file` are mutually exclusive 

**Examples**
```
> python disable_users.py --file users.txt

> python disable_users.py --user "John Smith"
```

## find_labs_for_keyword.py ##
This script returns a list of relevant labs for the given keyword or phrase.

**Usage**

`find_labs_for_keyword.py [-h] --keyword KEYWORD [--format FORMAT]`

* `--keyword` the search word or phrase
* `--format` indicates the output format. Valid values are JSON and CSV. The default is JSON.

**Examples**
```
> python find_labs_for_keyword.py --keyword CWE-117

> python find_labs_for_keyword.py --keyword "OWASP #8" --format CSV
```

## get_assigned_labs.py ##
This script retrieves all labs that are assigned in live campaigns, including labs for assignments that haven't started yet. Output is in JSON format.

**Usage**

`get_assigned_labs.py`

NOTE: No arguments for this script.

**Examples**
```
> python get_assigned_labs.py
```

## get_users_for_role.py ##
This script returns the list of users for a given role.

**Usage**

`get_users_for_role.py [-h] --role ROLE [--format FORMAT]`

* `--role` the role name (exact case required)
* `--format` indicates the output format. Valid values are JSON and CSV. The default is JSON.

**Examples**
```
> python get_users_for_role.py --role "New Hires"

> python get_users_for_role.py --role "Mobile App Developer" --format CSV
```

## invite_users.py ##
This script invites people to join Security Labs. Invited users are automatically assigned the default role(s). Use with standalone accounts, not platform-integrated accounts. Otherwise it can result in orphaned users.

**Usage**

`invite_users.py [-h] --file FILE --invited_by INVITED_BY [--send_email SEND_EMAIL]`

* `--file` a CSV file containing a list of people to invite (email, name) in two columns where email is required and name is optional. 
* `--invited_by` the name or ID of the Security Labs administrator who is creating the invitation 
* `--send_email` whether or not to send the activation email. Valid values are true or false. The default is true.

**Examples**
```
> python invite_users.py --file users.txt --invited_by "Dave Ferguson"

> python invite_users.py --file users.csv --invited_by 620d7333f6a514002fc7c499 --send_email false
```
