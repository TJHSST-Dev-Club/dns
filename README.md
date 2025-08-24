# TJ Dev Club DNS

DNS-as-code for [`tjdev.club`](https://tjdev.club). We keep our DNS records in YAML and deploy them to Cloudflare with OctoDNS. 

### What's Here?
- **Zone config**: Per-website-group YAML files live under `club_sites/` and `user_sites/`. A small build step merges them into `zones/tjdev.club.yaml` for OctoDNS.
- **Deploy**: GitHub Actions runs OctoDNS on pushes to `main` and applies changes to Cloudflare.
- **Scripts**: `deploy_dns.sh` (apply) and `dump_dns.sh` (export current zone). Both require Cloudflare creds.
- **Env**: Python 3.12 with `uv`. Deps are OctoDNS and the Cloudflare provider (see `pyproject.toml`).

### How it works
- We define records in YAML by group. Place one file per website group inside `club_sites/` or `user_sites/` (e.g., `club_sites/purelymail.yaml`, `club_sites/www.yaml`).
- `uv run python ./merge_zones.py` merges all YAML into `zones/tjdev.club.yaml`.
- CI runs: `octodns-sync --config-file=config/production.yaml --doit` to push changes using the merged zone.
- You don’t need Cloudflare access to propose changes; CI handles the deploy after merge.

### Add your subdomain (members)
1. Pick a subdomain (example: `jimmy.tjdev.club`).
2. Create a new file in `user_sites/` named after your group (e.g., `user_sites/jimmy.yaml`) with:

```yaml
---
jimmy:
  ttl: 300
  type: CNAME
  value: user.tjhsst.edu.
```

> [!IMPORTANT]
> When using FQDNs (like `user.tjhsst.edu.`), include the trailing dot. This tells DNS it's a fully qualified domain name, not relative to the current zone.

### Contribute via PR
- Fork this repository and make a branch with your change (usually a new or updated file under `user_sites/`).
- Keep the diff small and explain the “why” in the PR description.
- For shared/club records, mention an owner/contact.
- Avoid apex/root changes unless you're working on a club site!

### Optional local setup
- Install `uv`, then:

```bash
uv sync
uv run octodns-sync --config-file=config/production.yaml --help
```

- To export the current Cloudflare zone to files (requires secrets): `./dump_dns.sh`
- To deploy from local (requires secrets): `./deploy_dns.sh`

Questions? Open an issue or ask in the club Discord.
