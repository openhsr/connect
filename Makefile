#.PHONY: lean all
DOCKER_UID=1000
DOCKER_GID=1000

PASS_DIR?=$(shell readlink -f "./../pass" || (echo "Could not find PASS_DIR, please set it as env variable." >&2 && exit 2))
CONNECT_VERSION=$(shell git describe --tags 2> /dev/null || echo "0.0.1")

ifndef VERBOSE
.SILENT:
endif

TARGETS=$(shell find ./packaging/ -mindepth 2 -maxdepth 2 -type d | sed "s/^.\/packaging\///")

all: $(TARGETS)

$(TARGETS):
	$(eval TARGET_DIR=$(subst /, ,$@))
	$(eval export DISTRIBUTION=$(word 1,$(TARGET_DIR)))
	$(eval export VERSION=$(word 2,$(TARGET_DIR)))
	$(eval BUILDDIR=./packaging/$(DISTRIBUTION)/$(VERSION))
	$(eval DOCKERFILE=$(BUILDDIR)/Dockerfile)

	[ -f $(DOCKERFILE) ] || (echo "Error, no distribution with this name: $(DOCKERFILE)" >&2 && exit 1)
	# Build container
	docker build \
	    -t "openhsr/openhsr-connect-$(DISTRIBUTION)-$(VERSION)" \
	    --build-arg DOCKER_UID=$(DOCKER_UID) --build-arg DOCKER_GID=$(DOCKER_GID) \
		--build-arg VERSION --build-arg DISTRIBUTION \
	    -f $(DOCKERFILE) .

	# Build connect, dependencies and repositories
	mkdir -p $(shell pwd)/dist/$(DISTRIBUTION)/$(VERSION)/
	export PASSWORD_STORE_DIR=$(PASS_DIR) && \
		export GPG_KEY=`pass show connect/signkey` && \
		docker run -ti --rm --name "openhsr-connect-$(DISTRIBUTION)-$(VERSION)" \
		--volume=$(shell pwd)/dist/$(DISTRIBUTION)/:/repo/:rw \
	    --env GPG_KEY --env CONNECT_VERSION=$(CONNECT_VERSION) \
	    openhsr/openhsr-connect-$(DISTRIBUTION)-$(VERSION)


