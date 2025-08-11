#!/bin/bash

ENV_FILE="/root/actions-runner/.cache/set_env.sh"

echo "GITHUB_WORKSPACE=${GITHUB_WORKSPACE}"
docker exec \
  ascend_ci_a3 \
  /bin/bash -c "source \"$ENV_FILE\" && export PYTHONPATH=\"${GITHUB_WORKSPACE//\\/\/}/python:\${PYTHONPATH:-}\" && exec \"\$@\"" \
  bash "$@"