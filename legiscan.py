import os
import json
from urllib.parse import urlencode
from urllib.parse import quote_plus
import requests
import codes

class LegiScanError(Exception):
    pass

class LegiScan:
    BASE_URL = 'https://api.legiscan.com/?key={0}&op={1}&{2}'

    def __init__(self, apikey=None):
        '''Create API connection instance'''
        if apikey is None:
            apikey = os.environ['LEGISCAN_API_KEY']
        self.key = apikey.strip()

    def _url(self, operation, params=None):
        '''Build query URL'''
        if not isinstance(params, str) and params is not None:
            params = urlencode(params)
        elif params is None:
            params = ''
        return self.BASE_URL.format(self.key, operation, params)

    def _get(self, url):
        '''Make request and parse response'''
        req = requests.get(url)
        if not req.ok:
            raise LegiScanError('Request returned {0}: {1}'\
                    .format(req.status_code, url))
        data = json.loads(req.content)
        if data['status'] == 'ERROR':
            raise LegiScanError(data['alert']['message'])
        return data

    def get_session_list(self, state=None):
        '''Get list of legislative sessions in the specified state.'''
        if state is not None:
            url = self._url('getSessionList', {'state':state})
        else:
            raise ValueError('Must specify state to get session list.')
        data = self._get(url)
        return data['sessions']

    def get_master_list(self, state=None, session_id=None):
        '''Get list of bills in the current session for a state or
        given session identifier'''
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
        '''Get a list of bills in the current session for a state or 
        session identifier - only bill change_hash values.'''
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
        '''Get information for a single bill. Expects a bill_id (unique across all states/sessions).'''
        if bill_id is not None:
            url = self._url('getBill', {'id':bill_id})
        else:
            raise ValueError('Must specify id.')
        data = self._get(url)
        return data['bill']

    def get_bill_text(self, doc_id=None):
        '''Get bill text (base64 encoded to allow for PDF and Word data transfers)'''
        if doc_id is not None:
            url = self._url('getBillText', {'id':doc_id})
        else:
            raise ValueError('Must specify doc_id to retrieve bill text.')
        data = self._get(url)
        return data['text']

    def get_amendment(self, amendment_id=None):
        '''Get information for a single amendment.'''
        if amendment_id is not None:
            url = self._url('getAmendment', {'id':amendment_id})
        else:
            raise ValueError('Must specify an amendment ID.')
        data = self._get(url)
        return data['amendment']

    def get_supplement(self, supplement_id=None):
        '''Get information for a single bill supplement (e.g. fiscal note,
        veto letter).'''
        if supplement_id is not None:
            url = self._url('getSupplement', {'id':supplement_id})
        else:
            raise ValueError('Must specify a supplement ID.')
        data = self._get(url)
        return data['supplement']

    def get_roll_call(self, roll_call_id=None):
        '''Get roll call detail for individual votes.'''
        if roll_call_id is not None:
            url = self._url('getRollcall', {'id':roll_call_id})
        else:
            raise ValueError('Must specify roll_call_id to retrieve rollcall vote.')
        data = self._get(url)
        return data['roll_call']
    
    def get_person(self, people_id=None):
        '''Get person information'''
        if person_id is not None:
            url = self._url('getPerson', {'people_id':people_id})
        else:
            raise ValueError('Must specify people_id to retrieve people record.')
        data = self._get(url)
        return data['person']

    def search(self, state, bill_number=None, query=None, year=2, page=None):
        '''
        Get a page of results for a search against the Legiscan full text engine.
        Returns a paginated results set. 

        Specify a bill number or query string. Year can be an exact year or a number
        between 1 and 4 inclusive, where the numbers have the following meanings:
            1 = all years
            2 = current year (default)
            3 = recent years
            4 = prior years
        Page is the result set page number to return.
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
        '''Use the raw search function for keyword monitoring. 'state' and 'query' (search
        term) are the only required fields. 'year' and 'page' have the same meaning as in
        the /search/ method. 'relevance' is an integer from 1-100 indicating the judged
        relevance that the returned bill has to the search term. You can set the 'relevance'
        field to some minimum threshold or leave it blank to return all results.'''
        if query is not None:
            params = {'state':state, 'query':query, 'year':year, 'page':page}
        else:
            raise ValueError('Must specify query parameters for bill search.')
        if not isinstance(relevance, int) or relevance > 100 or relevance < 0:
            raise ValueError("Must specify valid value for relevance (integer 0-100).")
        data = self._get(self._url('searchRaw', params))['searchresult']
        # Return summary of the search and results with relevance scores
        summary = data.pop('summary')
        if relevance is not None:
            results = {'summary':summary, 'results':[r for r in data['results'] if r['relevance'] >= relevance]}
        else:
            results = {'summary':summary, 'results':[r for r in data['results']]}
        return results

    def get_dataset_list(self, state=None, year=None):
    	'''Get a list of available session datasets. 'state' and 'year' are optional parameters
    	and do not need to be specified for a search.'''
    	params = {'state':state, 'year':year}
    	data = self._get(self._url('getDatasetList', params))
    	return data['datasetlist']

    def get_dataset(self, session_id=None, access_key=None):
    	'''Get zipfile associated with a legislative session dataset.'''
    	if session_id is None or access_key is None:
    		raise ValueError('Must specify session_id and access_key to access dataset.')
    	params = {'id':session_id, 'access_key':access_key}
    	data = self._get(self._url('getDataset', params))
    	return data['dataset']
    
    def get_session_people(self, session_id=None):
        '''Get a list of people (legislators) associated with a single legislative session.'''
        if session_id is None:
            url = self._url('getSessionPeople', params={'session_id':session_id})
        else:
            raise ValueError('Must specify a session_id to get list of people associated with session.')
        data = self._get(url)
        return data['sessionpeople']
    
    def get_sponsored_list(self, people_id=None):
        '''Get list of bills sponsored by a single legislator.'''
        if people_id is not None:
            url = self._url('getSponsoredList', params={'people_id':people_id})
        else:
            raise ValueError('Must specify a people_id to get a list of bills sponsored by the individual.')
        data = self._get(url)
        return data['sponsoredbills']

    def __str__(self):
        return '<LegiScan API {0}>'.format(self.key)

    def __repr__(self):
        return str(self)