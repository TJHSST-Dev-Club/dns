 #!/bin/bash
 
# load variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# build merged zone (so config points at zones/)
uv run python ./../merge_zones.py || exit 1

# run octodns-dump
octodns-dump --config-file ./../config/production.yaml --output-dir ./../zone tjdev.club. cloudflare
