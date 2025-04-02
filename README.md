this repository contains a prototype gemini capsule for All Things Linux. until further notice, consider it licensed All Rights Reserved, though a license will be added if we decide to move forward with this as a project.

##Setup instructions:
1. Clone this repository
1. run `git submodule update --init --recursive`
1. replace the config.toml in the gemserv submodule with the one included in this repository. if you're running this outside of ATL prod, edit it to reflect your domain names.
1. run `docker compose up -d

## updating
1. run `git pull`. if config.toml is modified, commit and rebase it.
1. run `git restore gemserv/config.toml`
1. run `git submodule update --remote`
1. copy your config.toml back into the gemserv directory
1. run `docker compose down && docker compose up -d`
