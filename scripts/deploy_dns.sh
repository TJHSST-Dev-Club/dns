 #!/bin/bash
 
# load variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# build merged zone
uv run python ./../merge_zones.py || exit 1

# run octodns-sync
octodns-sync --config-file ./../config/production.yaml --doit
