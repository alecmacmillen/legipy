BILL_CODES = {1:'Bill', 2:'Resolution', 3:'Concurrent Resolution', 
              4:'Joint Resolution', 5:'Joint Resolution Constitutional Amendment',
              6:'Executive Order', 7:'Constitutional Amendment', 8:'Memorial',
              9:'Claim', 10:'Commendation', 11:'Committee Study Request',
              12:'Joint Memorial', 13:'Proclamation', 14:'Study Request',
              15:'Address', 16:'Concurrent Memorial', 17:'Initiative',
              18:'Petition', 19:'Study Bill', 20:'Initiative Petition',
              21:'Repeal Bill', 22:'Remonstratin', 23:'Committee Bill'}

MIME_CODES = {1:'HTML', 2:'PDF', 3:'WordPerfect', 4:'MS Word (.doc)',
              5:'Rich Text Format', 6:'MS Word 2007 (.docx)'}

PARTY_CODES = {1:'Democrat', 2:'Republican', 3:'Independent', 4:'Green',
               5:'Libertarian', 6:'Nonpartisan'}

REASON_CODES = {1:'New legislation', 2:'Status value changed', 3:'Bill moved chambers',
                4:'Bill completed legislative action', 5:'Title changed',
                6:'Description changed', 7:'Referred or re-referred to committee',
                8:'Reported from committee', 9:'Sponsor was added', 
                10:'Sponsor was removed', 11:'Existing sponsor position / type changed',
                12:'New history steps were added', 13:'History steps have been removed',
                14:'Prior history steps have been revised', 
                15:'History changes included major steps', 
                16:'History changes included minor steps',
                17:'Subject was added', 18:'Subject was removed', 
                19:'New SAST bill associated', 20:'New bill text document',
                21:'New amendment document', 22:'New supplement document',
                23:'New vote record', 24:'New/updated calendar event',
                25:'Progress array has been updated'}

ROLE_CODES = {1:'Representative / Lower Chamber', 2:'Senator / Upper Chamber',
              3:'Joint Conference'}

SAST_CODES = {1:'Same As', 2:'Similar To', 3:'Replaced By', 4:'Replaces', 
              5:'Cross-filed', 6:'Enabling for', 7:'Enabled by', 8:'Related',
              9:'Carry Over'}

SPONSOR_CODES = {0:'Sponsor (Generic / Unspecified)', 1:'Primary Sponsor', 
                 2:'Co-Sponsor', 3:'Joint Sponsor'}

STATUS_CODES = {1:'Introduced', 2:'Engrossed', 3:'Enrolled', 4:'Passed', 5:'Vetoed',
                6:'Failed', 7:'Override', 8:'Chaptered', 9:'Refer', 10:'Report Pass',
                11:'Report DNP', 12:'Draft'}

SUPPLEMENT_CODES = {1:'Fiscal Note', 2:'Analysis', 3:'Fiscal Note/Analysis', 4:'Vote Image',
                    5:'Local Mandate', 6:'Corrections Impact', 7:'Miscellaneous', 8:'Veto Letter'}

TEXT_CODES = {1:'Introduced', 2:'Committee Substitute', 3:'Amended', 4:'Engrossed', 5:'Enrolled',
              6:'Chaptered', 7:'Fiscal Note', 8:'Analysis', 9:'Draft', 10:'Conference Substitute',
              11:'Prefiled', 12:'Veto Message', 13:'Veto Response', 14:'Substitute'}

VOTE_CODES = {1:'Yea', 2:'Nay', 3:'Not Voting / Abstain', 4:'Absent / Excused'}