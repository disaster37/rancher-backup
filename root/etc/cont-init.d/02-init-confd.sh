#!/usr/bin/with-contenv bash

if [ "${CONFD_NODES}X" == "X" ]; then
  NODE=""
else
  NODE="-node ${CONFD_NODES}"
fi

${CONFD_HOME}/bin/confd -confdir ${CONFD_HOME}/etc -onetime -backend ${CONFD_BACKEND} ${PREFIX} ${NODE}
