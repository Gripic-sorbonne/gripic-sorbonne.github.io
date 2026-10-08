echo "Fetching data in HAL"
var_date=$(date +"%Y%m%d")
##google-chrome https://hal.archives-ouvertes.fr/search/index/?qa%5BstructAcronym_t%5D%5B%5D=STIH&submit_advanced=Rechercher&rows=30
wget "http://api.archives-ouvertes.fr/search/?q=structAcronym_t:STIH;&rows=9000&wt=bibtex" -O $var_date.bib
echo "--Done--"

## tester : https://api.archives-ouvertes.fr/search/hal/?omitHeader=true&wt=bibtex&q=structAcronym_t%3A%28STIH%29&fq=NOT+instance_s%3Asfo&fq=NOT+instance_s%3Adumas&fq=NOT+instance_s%3Amemsic&fq=NOT+instance_s%3Ahceres&fq=NOT+%28docType_s%3A%28THESE+OR+HDR%29+AND+submitType_s%3A%28notice+OR+annex%29%29&fq=NOT+docType_s%3A%28MEM+OR+PRESCONF+OR+MINUTES+OR+NOTE+OR+SYNTHESE+OR+OTHERREPORT+OR+REPACT+OR+BOOKREPORT%29&fq=NOT+status_i%3A111&defType=edismax&rows=1000

echo "Next : pandoc-citeproc --bib2json "
pandoc-citeproc --bib2json $var_date.bib >$var_date.bib.json
echo "--Done--"

echo "copying to STIH_last_publis.json"
cp $var_date.bib.json STIH_last_publis.json
echo "--Done--"

echo "--> Now run model2html"
