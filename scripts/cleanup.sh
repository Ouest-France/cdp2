#/bin/bash

NAMESPACE=
RELEASE=
usage() { echo "Usage: $0 [-n <namespace>] -r <release>" 1>&2; exit 4; }

while getopts "n:r:" option; do
    case "${option}" in
        n)
            TILLER_NAMESPACE_LIST="--tiller-namespace ${OPTARG}"
            TILLER_NAMESPACE_MIGR="-t ${OPTARG}";;
        r)
            RELEASE=${OPTARG};;
        *)
            usage
            ;;
    esac
done

if [ "$RELEASE" == "" ]; then
   usage
fi

helm3 2to3 cleanup ${TILLER_NAMESPACE_MIGR} --name ${RELEASE} --skip-confirmation
if [ ! $? -eq 0 ];then
   echo "Erreur lors du cleanup de la release ${RELEASE}"
   exit 2
fi
if [ "$(helm2 ${TILLER_NAMESPACE_LIST} list -q| wc -l)" == "0" ]; then
   echo -e "\e[101m===================================================\e[0m"
   echo -e "\e[101m= No release hold by Helm2. Tiller can be deleted =\e[0m"
   echo -e "\e[101m===================================================\e[0m"
#
#   # Derniere release : On cleanup le namespace
#   helm3 2to3 cleanup -t ${NAMESPACE} --skip-confirmation
#   if [ ! $? -eq 0 ]; then
#      echo "Erreur lors du cleanup du namespace ${NAMESPACE}"
#      exit 2
#   fi 
fi
echo "Cleanup de la release ${RELEASE} effectuee"
