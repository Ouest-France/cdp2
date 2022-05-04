#/bin/bash

NAMESPACE=
RELEASE=
TILLER_NAMESPACE=
usage() { echo "Usage: $0 -n <namespace> -r <release> [-t<namespace>]" 1>&2; exit 4; }

while getopts "n:r:t:" option; do
    case "${option}" in
        n)
            NAMESPACE=${OPTARG};;
        r)
            RELEASE=${OPTARG};;
        t)
            TILLER_NAMESPACE_LIST="--tiller-namespace ${OPTARG}"
            TILLER_NAMESPACE_MIGR="-t ${OPTARG}";;
        *)
            usage
            ;;
    esac
done

if [ "$RELEASE" == "" -o "$NAMESPACE" == "" ]; then
   usage
fi

RELEASEV3=$(helm3 list -qn ${NAMESPACE} -f "^${RELEASE}$")
if [ ! $? -eq 0 ]; then
   echo "Erreur dans la migration de la release ${RELEASE}"
   exit 2
fi
if [ "$RELEASEV3" == "" ]; then
   # Test s'il y a une release V2. Sinon, c'est une nouvelle release
   RELEASEV2=$(helm2 ${TILLER_NAMESPACE_LIST} list -q "^${RELEASE}$")
   if [ "$RELEASEV2" != "" ]; then
      # Migration release
      helm3 2to3 convert ${TILLER_NAMESPACE_MIGR} ${RELEASE}
      if [ ! $? -eq 0 ]; then
         echo "Erreur dans la migration de la release ${RELEASE}"
         exit 2
      fi
  
      RELEASEV3=$(helm3 list -qn ${NAMESPACE} -f "^${RELEASE}$")
      if [  ! $? -eq 0 -o "$RELEASEV3" == "" ]; then
         echo "Erreur dans la migration de la release ${RELEASE}"
         exit 3
      fi
      echo "Release $2 migree en Helm3"
      exit 1
   fi
fi
