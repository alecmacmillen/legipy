# legipy
## Background
[LegiScan](https://legiscan.com/legiscan) is an online legislative tracking service. Users of LegiScan can look up bills, legislative sessions, legislators, and more at both the federal (US Congress) and state level. LegiScan provides an API that allows users to make structured HTTP requests for information, which is then delivered as a JSON object. The goal of this repository is to create a simple Python class that "wraps around" the LegiScan API to simplify the process of making API calls.

This repository contains two files: `legiscan.py` has the implementation of the main API wrapper class, and `codes.py` has a series of dictionaries that translate codes for various LegiScan concepts (for example, bill statuses, bill sponsors, etc.) As of May 21, 2021, this code is not yet available for installation from Python Package Index (PyPI). This repository must be cloned and the files saved locally before importing into your code for use.

## Using the Module
Once you have cloned this repository and saved `legiscan.py`, you can import the API wrapper class directly into your Python code:

`from legiscan import LegiScan`

To use the LegiScan API you must [register](https://legiscan.com/user/register) with LegiScan and request an API key. Both registration and key request are free, and LegiScan allows 30,000 free requests per month. Once you have your API key you can either set it as an environment variable or pass it explicitly to the class constructor:

`legis = LegiScan() #if you set your API key as an environment variable`
`legis = LegiScan(apikey=YOUR_API_KEY_HERE) #if you are passing your key explicitly`

To test whether your API key is working, you can run this request to get a list of all available sessions of information in the state of Illinois:

`legis.get_session_list(state='IL')`

Now you can use your `legis` object to perform any API calls that LegiScan makes available. Consult LegiScan's [API user manual](https://legiscan.com/misc/LegiScan_API_User_Manual.pdf) for more information. Broadly speaking, LegiScan API operations presented in the manual in `CamelCase` are available as class methods in `snake_case`. As an example, the `getBillText` operation would be called using `legis.get_bill_text(**params)`. A full list of operations available is below, and you can get guidance on usage by running `help(LegiScan.METHOD_NAME)` from within Python once you have imported the module (or run `help(LegiScan)` to see all the docstrings at once).

- `get_session_list`
- `get_master_list`
- `get_master_list_raw`
- `get_bill`
- `get_bill_text`
- `get_amendment`
- `get_supplement`
- `get_roll_call`
- `get_person`
- `search`
- `search_raw`
- `get_dataset_list`
- `get_session_people`
- `get_sponsored_list`

Under the hood, the `LegiScan` class performs its methods by dynamically constructing API query strings, making HTTP requests using those strings, and parsing the JSON responses into Python dictionaries or lists of dictionaries, where appropriate. If there is an error in your request or the HTTP response, an error message with a hint about what went wrong will be printed.

## A Worked Example
In this example, we use the `LegiScan` class to build a list of all bills sponsored by Republicans in the 2021 session of the Texas state senate. Start by importing modules and setting up an instance of the `LegiScan` class.

```
from legiscan import LegiScan

legis = LegiScan(apikey=YOUR_API_KEY_HERE)
```

Next, get a list of all Republicans in the Texas state senate during the 2021 session. We have to start by identifying the appropriate `session_id` from a call to `get_session_list`.

```
tx_sessions = legis.get_session_list(state='TX')
tx_session_id = tx_sessions[0]['session_id']
```

Now we can get a list of Republicans from `get_session_people`. For each person returned by the `get_session_people` call, we can check their party and role IDs and append their `people_id` to a list if they are Republican senators.

```
tx_sessionpeople = legis.get_session_people(session_id=tx_session_id)
r_senators = []
for person in tx_sessionpeople['people']:
    if person['party'] == 'R' and person['role'] == 'Sen':
        r_senators.append(person['people_id'])
```

The next step is to run through all Republican senators and get a list of bills they sponsored, keeping track to avoid duplicates.

```
full_bill_id_list = []
for people_id in r_senators:
    sponsored_list = legis.get_sponsored_list(people_id=people_id)
    for bill in sponsored_list['bills']:
        if bill['session_id'] == tx_session_id and bill['bill_id'] not in full_bill_id_list:
            full_bill_id_list.append(bill['bill_id'])
```

Finally, we can get all the relevant information about the list of sponsored bills.

```
full_bill_list = []
for bill_id in full_bill_id_list:
    bill_detail = legis.get_bill(bill_id=bill_id)
    full_bill_list.append(bill_detail)
```

## Acknowledgements
This repository expands on work done by [Chris Poliquin's pylegiscan repository](https://github.com/poliquin/pylegiscan).