.PHONY: all upload
DOCKER_UID=1000
DOCKER_GID=1000
CONNECT_VERSION=$(shell ./packaging/version.bash)
BUILDDIR=./packaging/$(DISTRIBUTION)/$(VERSION)
DOCKERFILE=$(BUILDDIR)/Dockerfile

ifndef GPG_KEY
PASS_DIR?=$(shell readlink -f "./../pass" || (echo "Could not find PASS_DIR, please set it as env variable." >&2 && exit 2))
export GPG_KEY=$(shell PASSWORD_STORE_DIR=$(PASS_DIR) pass show  pool/gpg_pool@openhsr.ch_PRIVATE_key | awk 1 ORS='\\n' -)
endif


ifndef VERBOSE
.SILENT:
endif

TARGETS=$(shell find ./packaging/ -mindepth 2 -maxdepth 2 -type d | sed "s/^.\/packaging\///")

all: $(TARGETS)

$(TARGETS):
	@echo ========================================================================
	@echo Building version $(CONNECT_VERSION) for $@
	@echo ========================================================================
	[ "$(GPG_KEY)" != "" ] || (echo "Could not find GPG_KEY, please set it as env variable or fix pass repository." >&2 && exit 3)
	$(eval export DISTRIBUTION=$(word 1,$(subst /, ,$@)))
	$(eval export VERSION=$(word 2,$(subst /, ,$@)))

	[ -f $(DOCKERFILE) ] || (echo "Error, no distribution with this name: $(DOCKERFILE)" >&2 && exit 1)
	# Build container
	docker build \
	    -t "openhsr/openhsr-connect-$(DISTRIBUTION)-$(VERSION)" \
	    --build-arg DOCKER_UID=$(DOCKER_UID) --build-arg DOCKER_GID=$(DOCKER_GID) \
	    --build-arg VERSION --build-arg DISTRIBUTION \
	    -f $(DOCKERFILE) .

	# Build connect, dependencies and repositories
	mkdir -p $(shell pwd)/dist/$(DISTRIBUTION)/$(VERSION)/
	export GPG_KEY="$(GPG_KEY)" && docker run -ti --rm --name "openhsr-connect-$(DISTRIBUTION)-$(VERSION)" \
	    --volume=$(shell pwd)/dist/$(DISTRIBUTION)/:/repo/:rw \
	    --env GPG_KEY --env CONNECT_VERSION=$(CONNECT_VERSION) \
	    openhsr/openhsr-connect-$(DISTRIBUTION)-$(VERSION)

upload:
	cp packaging/htaccess dist/.htaccess
	cp packaging/pool@openhsr.ch.gpg.key dist/
	docker build -f packaging/Dockerfile.lftp -t openhsr/deploy packaging/	
	docker run -it -e USER -e PASSWORD -e HOST -e DIR_REMOTE --rm -v $(shell pwd)/dist:/repo openhsr/deploy
