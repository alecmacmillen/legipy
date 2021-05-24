import os
import json
from urllib.parse import urlencode
from urllib.parse import quote_plus
import requests

class LegiScanError(Exception):
    pass

class LegiScan:
    BASE_URL = 'https://api.legiscan.com/?key={0}&op={1}&{2}'

    def __init__(self, apikey=None):
        '''
        Inputs: 
            apikey (str, default None)
        Outputs:
            None (creates instance of the class)

        Create API connection instance. If apikey parameter is None, you
        must have your LegiScan API key stored as an environment variable.
        '''
        if apikey is None:
            apikey = os.environ['LEGISCAN_API_KEY']
        self.key = apikey.strip()

    def _url(self, operation, params=None):
        '''
        Inputs: 
            operation (str; required)
            params (dict, default None)
        Outputs:
            query URL string

        Build query URL. This is a helper method called by all main methods.
        The 'operation' parameter is the name of a LegiScan API operation
        and 'params' are the relevant parameters specified as a dictionary
        (e.g. params={'state':'IL'} would set the operation parameters to 
        the state of Illinois).)
        '''
        if not isinstance(params, str) and params is not None:
            params = urlencode(params)
        elif params is None:
            params = ''
        return self.BASE_URL.format(self.key, operation, params)

    def _get(self, url):
        '''
        Inputs:
            url (str; required)
        Outputs:
            Parsed API response data

        Make request and parse response. This is a helper method used by all
        main methods. Uses the url formatted by the _url method to make the 
        HTTP request, then parses the JSON response and returns either the 
        data payload or an error message. 
        '''
        req = requests.get(url)
        if not req.ok:
            raise LegiScanError('Request returned {0}: {1}'\
                    .format(req.status_code, url))
        data = json.loads(req.content)
        if data['status'] == 'ERROR':
            raise LegiScanError(data['alert']['message'])
        return data

    def get_session_list(self, state=None):
        '''
        Inputs:
            state (str; required)
        Outputs:
            List of legislative sessions for specified state (list of dicts)

        Get list of legislative sessions in the specified state. You must
        specify a single state using its two-character postal code.
        '''
        if state is not None:
            url = self._url('getSessionList', {'state':state})
        else:
            raise ValueError('Must specify state to get session list.')
        data = self._get(url)
        return data['sessions']

    def get_master_list(self, state=None, session_id=None):
        '''
        Inputs:
            state (str)
            session_id (int or str)
            You must specify AT LEAST ONE of state and/or session_id
        Outputs:
            dictionary with keys 'session' and 'bills'
                'session': dictionary with session information
                'bills': list of dicts with each dict representing one bill's
                    information
        
        Get list of bills in the current session for a state or given session 
        identifier. If only state is provided, the output will default to the
        most recent legislative session. 
        '''
        if state is not None:
            url = self._url('getMasterList', {'state':state})
        elif session_id is not None:
            url = self._url('getMasterList', {'id':session_id})
        else:
            raise ValueError('Must specify session identifier or state.')
        data = self._get(url)
        session = data['masterlist'].pop('session')
        return {'session':session, 'bills':[b for b in data['masterlist'].values()]}
    
    def get_master_list_raw(self, state=None, session_id=None):
        '''
        Inputs:
            state (str)
            session_id (int or str)
            You must specify AT LEAST ONE of state and/or session_id
        Outputs:
            dictionary with keys 'session' and 'bills'
                'session': dictionary with session information
                'bills': list of dicts with each dict representing one bill's
                    information. Includes ONLY bill_id, number, and change_hash.

        Get a list of bills in the current session for a state or session
        identifier. The "raw" operation includes only a change_hash value that
        you can use to track bill changes (does not include more detailed bill
        information).
        '''
        if state is not None:
            url = self._url('getMasterListRaw', {'state':state})
        elif session_id is not None:
            url = self._url('getMasterListRaw', {'id':session_id})
        else:
            raise ValueError('Must specify session identifier or state.')
        data = self._get(url)
        session = data['masterlist'].pop('session')
        return {'session':session, 'bills':[b for b in data['masterlist'].values()]}

    def get_bill(self, bill_id=None):
        '''
        Inputs:
            bill_id (int or str; required)
        Outputs: 
            dictionary of bill information with the following keys:
                'bill_id', 'change_hash', 'session_id', 'session', 'url', 
                'state_link', 'completed', 'status', 'status_date', 'progress',
                'state', 'state_id', 'bill_number', 'bill_type', 'bill_type_id',
                'body', 'body_id', 'current_body', 'current_body_id', 'title',
                'description', 'committee', 'pending_committee_id', 'history',
                'sponsors', 'sasts', 'subjects', 'texts', 'votes', 'amendments',
                'supplements', 'calendar'

        Get information for a single bill. Requires a single bill_id value 
        (bill_ids are unique identifiers across all states/sessions). Returns a
        single dict with detailed, in-depth information on the contents and 
        status of requested bill.
        '''
        if bill_id is not None:
            url = self._url('getBill', {'id':bill_id})
        else:
            raise ValueError('Must specify id.')
        data = self._get(url)
        return data['bill']

    def get_bill_text(self, doc_id=None):
        '''
        Inputs: 
            doc_id (int or str; required)
        Outputs:
            dictionary of bill document information including the
            following keys:
                'doc_id', 'bill_id', 'date', 'type', 'type_id', 'mime',
                'mime_id', 'text_size', 'doc'
        
        Get bill text (value for 'doc' key, base64 encoded to allow for PDF 
        and Word data transfers). The doc_id value can be found in the value 
        related to the 'texts' key in the output of a call to get_bill().
        '''
        if doc_id is not None:
            url = self._url('getBillText', {'id':doc_id})
        else:
            raise ValueError('Must specify doc_id to retrieve bill text.')
        data = self._get(url)
        return data['text']

    def get_amendment(self, amendment_id=None):
        '''
        Inputs:
            amendment_id (str or int; required)
        Outputs:
            dictionary of amendment information for a single amendment to a 
            bill, including the following keys:
                'amendment_id', 'chamber', 'chamber_id', 'bill_id', 'adopted',
                'date', 'title', 'description', 'mime', 'mime_id', 'doc'
            
        Get information for a single amendment (the text of the amendment is
        stored in the 'doc' key and is base64 encoded to allow for PDF and Word
        data transfers). Values for a bill's amendment_ids can be found in the
        'amendments' key of the output from a call to get_bill().
        '''
        if amendment_id is not None:
            url = self._url('getAmendment', {'id':amendment_id})
        else:
            raise ValueError('Must specify an amendment ID.')
        data = self._get(url)
        return data['amendment']

    def get_supplement(self, supplement_id=None):
        '''
        Inputs:
            supplement_id (str or int; required)
        Outputs:
            dictionary of supplement information for a single supplement to a
            bill, including the following keys:
                'supplement_id', 'bill_id', 'date', 'type_id', 'type', 'title',
                'description', 'mime', 'mime_id', 'doc'
        
        Get information for a single bill supplement (e.g. fiscal note,
        veto letter, fact sheet, etc.). Values for a bill's supplement_ids can
        be found in the 'supplements' key of the output from a call to get_bill().
        '''
        if supplement_id is not None:
            url = self._url('getSupplement', {'id':supplement_id})
        else:
            raise ValueError('Must specify a supplement ID.')
        data = self._get(url)
        return data['supplement']

    def get_roll_call(self, roll_call_id=None):
        '''
        Inputs:
            roll_call_id (str or int; required)
        Outputs:
            dictionary of information for a single roll call vote on a bill,
            including the following keys:
                'roll_call_id', 'bill_id', 'date', 'desc', 'yea', 'nay', 'nv',
                'absent', 'total', 'passed', 'chamber', 'chamber_id', 'votes'
        
        Get roll call detail for individual votes. A list of available roll_call_id
        values for a given bill can be found in the 'votes' key of the output from
        a call to get_bill().
        '''
        if roll_call_id is not None:
            url = self._url('getRollcall', {'id':roll_call_id})
        else:
            raise ValueError('Must specify roll_call_id to retrieve rollcall vote.')
        data = self._get(url)
        return data['roll_call']
    
    def get_person(self, people_id=None):
        '''
        Inputs:
            people_id (str or int; required)
        Outputs:
            dictionary of information for a single person (legislator), including
            the following keys:
                'people_id', 'person_hash', 'state_id', 'party_id', 'party', 
                'role_id', 'role', 'name', 'first_name', 'middle_name', 
                'last_name', 'suffix', 'nickname', 'district', 'ftm_eid',
                'votesmart_id', 'opensecrets_id', 'ballotpedia', 
                'committee_sponsor', 'committee_id'
        
        Get information on attributes of a single person (legislator), identified
        by their unique people_id. 
        '''
        if people_id is not None:
            url = self._url('getPerson', {'people_id':people_id})
        else:
            raise ValueError('Must specify people_id to retrieve people record.')
        data = self._get(url)
        return data['person']

    def search(self, state, bill_number=None, query=None, year=2, page=None):
        '''
        Inputs:
            state (2-char postal code abbreviation; required)
            bill_number (str; optional)
            query (str; optional)
            year (str or int; optional)
            page (str or int; optional)
        Outputs:
            a dictionary with keys 'summary' (summary of results including number
            of bills returned, number of pages in results, and relevance range of
            returned bills); and
            'results', which contains a list of the bills that fall within the
            search parameters

        Get a page of results for a search against the Legiscan full text engine.
        Returns a paginated results set. You must specify a state code AND a 
        bill_number OR a search query, search year, and search page.

        Specify a bill number or query string. Year can be an exact year or a number
        between 1 and 4 inclusive, where the numbers have the following meanings:
            1 = all years
            2 = current year (default)
            3 = recent years
            4 = prior years
        Page is the number of result pages to return.
        '''
        if bill_number is not None:
            params = {'state':state, 'bill':bill_number}
        elif query is not None:
            params = {'state':state, 'query':query, 'year':year, 'page':page}
        else:
            raise ValueError('Must specify bill_number or query.')
        data = self._get(self._url('search', params))['searchresult']
        # Return a summary of the search and the results as a dict
        summary = data.pop('summary')
        results = {'summary':summary, 'results':[r for r in data['results']]}
        return results

    def search_raw(self, state, query=None, year=2, page=None, relevance=None):
        '''
        Inputs:
            state (2-char postal code abbreviation; required)
            query (str; required)
            year (str or int; optional)
            page (str or int; optional)
            relevance (str or int; optional)
        Outputs:
            a dictionary with keys 'summary' (summary of results including number
            of bills returned, number of pages in results, and relevance range of
            returned bills); and
            'results', which contains a list of the bills that fall within the
            search parameters

        Uses the raw search function for keyword monitoring. 'state' and 'query' (search
        term) are the only required fields. 'year' and 'page' have the same meaning as in
        the /search/ method. 'relevance' is an integer from 1-100 indicating the judged
        relevance that the returned bill has to the search term. You can set the 'relevance'
        field to some minimum threshold or leave it blank to return all results.
        '''
        if query is not None:
            params = {'state':state, 'query':query, 'year':year, 'page':page}
        else:
            raise ValueError('Must specify query parameters for bill search.')
        if not isinstance(relevance, int) or relevance > 100 or relevance < 0:
            raise ValueError(
                "Must specify valid value for relevance (integer 0-100).")
        data = self._get(self._url('searchRaw', params))['searchresult']
        # Return summary of the search and results with relevance scores
        summary = data.pop('summary')
        if relevance is not None:
            results = {'summary':summary, 'results':[
                r for r in data['results'] if r['relevance'] >= relevance]}
        else:
            results = {'summary':summary, 
                'results':[r for r in data['results']]}
        return results

    def get_dataset_list(self, state=None, year=None):
    	'''
        Inputs:
            state (2-char postal abbreviation; optional)
            year (int or string; optional)
        Outputs:
            list of dictionaries representing the datasets that are available
            from LegiScan, where each dictionary has the following keys:
                'state_id', 'session_id', 'special', 'year_start',
                'year_end', 'session_name', 'session_title', 'dataset_hash',
                'dataset_date', 'dataset_size', 'access_key'
        
        Get a list of available session datasets. 'state' and 'year' are 
        optional parameters and do not need to be specified for a search.
        '''
    	params = {'state':state, 'year':year}
    	data = self._get(self._url('getDatasetList', params))
    	return data['datasetlist']

    def get_dataset(self, session_id=None, access_key=None):
    	'''
        Inputs:
            session_id (str or int; required)
            access_key (access key from get_dataset_list operation for
                the session_id being requested; required)
        Outputs:
            dictionary with relevant information about the dataset being
            requested, including the following keys:
                'state_id', 'session_id', 'session_name', 'dataset_hash',
                'dataset_date', 'dataset_size', 'mime', 'zip'
        
        Get zipfile associated with a legislative session dataset. The 'zip'
        key of the returned dictionary contains the dataset in MIME 64
        Encoded ZIP Archive format.
        '''
    	if session_id is None or access_key is None:
    		raise ValueError(
                'Must specify session_id and access_key to access dataset.')
    	params = {'id':session_id, 'access_key':access_key}
    	data = self._get(self._url('getDataset', params))
    	return data['dataset']
    
    def get_session_people(self, session_id=None):
        '''
        Inputs:
            session_id (str or int; required)
        Outputs:
            dictionary with the following keys:
                'session', meta-information about the legislative session 
                'people', a list of dicts where each dict gives detailed 
                    information about a legislator in the session
        
        Get a list of people (legislators) associated with a single 
        legislative session.
        '''
        if session_id is not None:
            url = self._url('getSessionPeople', 
                params={'session_id':session_id})
        else:
            raise ValueError(
                'Must specify a session_id to get list of people.')
        data = self._get(url)
        return data['sessionpeople']
    
    def get_sponsored_list(self, people_id=None):
        '''
        Inputs:
            people_id (str or int; required)
        Outputs:
            dictionary with the following keys:
                'sponsor': dict with information about the legislator
                'sessions': list of dicts with information about sessions 
                    the legislator participated in
                'bills': list of dicts with information about bills
                    the legislator sponsored
        
        Get list of bills sponsored by a single legislator.
        '''
        if people_id is not None:
            url = self._url('getSponsoredList', params={'people_id':people_id})
        else:
            raise ValueError(
                'Must specify a people_id to get a list of bills sponsored.')
        data = self._get(url)
        return data['sponsoredbills']

    def __str__(self):
        return '<LegiScan API {0}>'.format(self.key)

    def __repr__(self):
        return str(self)