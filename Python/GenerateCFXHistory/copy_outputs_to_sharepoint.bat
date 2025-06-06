PUSHD Output

del /S /Q  "C:\Users\fr232487\OneDrive - Siemens AG\General - Projet Nexteo_ATS+\10 - KPI des lots\KPI CFX\*"
timeout /t 30

move "CFX_list_cyber_aio.txt*.html" "C:\Users\fr232487\OneDrive - Siemens AG\General - Projet Nexteo_ATS+\10 - KPI des lots\KPI CFX\CFX Cyber"

move "All cumulative *.html" "C:\Users\fr232487\OneDrive - Siemens AG\General - Projet Nexteo_ATS+\10 - KPI des lots\KPI CFX\Globaux"
move "*Project FR_NEXTEO.html" "C:\Users\fr232487\OneDrive - Siemens AG\General - Projet Nexteo_ATS+\10 - KPI des lots\KPI CFX\Projet NExTEO"
move "CFX_usine_site*.html" "C:\Users\fr232487\OneDrive - Siemens AG\General - Projet Nexteo_ATS+\10 - KPI des lots\KPI CFX\Projet NExTEO"
move "*Project ATSP.html" "C:\Users\fr232487\OneDrive - Siemens AG\General - Projet Nexteo_ATS+\10 - KPI des lots\KPI CFX\Projet ATSP"

timeout /t 30


