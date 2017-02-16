#.PHONY: lean all
.SILENT: .DEFAULT
DOCKER_UID=1000
DOCKER_GID=1000

TARGET=$(subst /, ,$@)
DISTRIBUTION=$(word 1,$(TARGET))
VERSION=$(word 2,$(TARGET))
BUILDDIR=./packaging/$(DISTRIBUTION)/$(VERSION)
DOCKERFILE=$(BUILDDIR)/Dockerfile

.DEFAULT:
	[ -f $(DOCKERFILE) ] || (echo "Error, no distribution with this name: $(DOCKERFILE)" >&2 && exit 1)
	# Build container
	docker build \
	    -t "openhsr/openhsr-connect-$(DISTRIBUTION)-$(VERSION)" \
	    --build-arg DOCKER_UID=$(DOCKER_UID) --build-arg DOCKER_GID=$(DOCKER_GID) \
		--build-arg VERSION=$(VERSION) --build-arg DISTRIBUTION=$(DISTRIBUTION) \
	    -f $(DOCKERFILE) .
	# Build connect, dependencies and repositories
	docker run --rm --name "openhsr-connect-$(DISTRIBUTION)-$(VERSION)" \
		--volume=$(shell pwd)/dist/$(DISTRIBUTION)/$(VERSION)/:/repo/:rw \
	    --env GPGKEY \
	    openhsr/openhsr-connect-$(DISTRIBUTION)-$(VERSION)
