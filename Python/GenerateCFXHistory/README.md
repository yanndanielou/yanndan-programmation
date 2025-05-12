# GenerateCFXHistory

```URI Rest:
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.
```

Rehercher un enregistreement, connexion automatique
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/{{recordId}}?format=HTML&loginId={{loginid}}&password={{password}}

https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/CFX00393065?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/RECORD/CFX00393065?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.&noframes=true

Executer un rapport
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/REPORT/Personal%20Queries/NExTEO%20%26%20ATS%2B/ATS%2B%20%26%20NExTEO%20details?format=HTML&loginId=AD001%5Cfr232487&password=Zzeerrttyy9.&noframes=true

Requête CCB:
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NEXTEO/ATS%2B%20%26%20NExTEO%20pour%20CMC?format=HTML&loginId={{loginid}}&password={{password}}&noframes=true

Changements états
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NExTEO_ATS_Courbes/NExteo_ATSp_changements_etats?format=HTML&loginId={{loginid}}&password={{password}}&noframes=true

Changements Owner
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NExTEO_ATS_Courbes/NExteo_ATSp_changements_owner?format=HTML&loginId={{loginid}}&password={{password}}&noframes=true

Etats
https://champweb.siemens.net/cqweb/restapi/01_CHAMP/CFX/QUERY/Personal%20Queries/NExTEO_ATS_Courbes/NExteo_ATSp_details?format=HTML&loginId={{loginid}}&password={{password}}&noframes=true




## Running Tests


## Installation

```sh
pip install .
pip install -e ..\Logger
pip install -e ..\Common
```

## Running Tests

```sh
pytest
```

