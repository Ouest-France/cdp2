#/bin/bash

NAMESPACE=
RELEASE=
usage() { echo "Usage: $0 -n <namespace> -r <release>" 1>&2; exit 4; }

while getopts "n:r:" option; do
    case "${option}" in
        n)
            NAMESPACE=${OPTARG};;
        r)
            RELEASE=${OPTARG};;
        *)
            usage
            ;;
    esac
done

if [ "$RELEASE" == "" -o "$NAMESPACE" == "" ]; then
   usage
fi

RELEASEV3=$(helm3 list -n ${NAMESPACE} --pending -f "^${RELEASE}$" | grep "pending-install")
if [ $? -eq 0 ]; then
   echo "La release est en cours d'installation ..."
   echo "Suppression de la release ..."
   helm3 uninstall $RELEASE -n ${NAMESPACE} 
fi
