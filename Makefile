.PHONY: help \
        build-proxy \
		build-all-proxies \
		build-app-backend \
		push-proxy \
		push-all-proxies \
		push-app-backend

# Terraform settings.
SRC = $(wildcard *.tf ./*/*.tf)
platform := $(shell uname)
pydeps := pyyaml boto3
modules = $(shell ls -1 ./*.tf ./*/*.tf | xargs -I % dirname %)

# Docker image name and tag. Build assumes ACCOUNT is set
# as an env var before running any commands.
TAG?=latest
SHELL:=bash

APP-BACKEND_IMAGE:=app-backend
ALL_PROXY_IMAGES:=nginx \
        traefik

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "=============================================="
	@echo "IllumiDesk docker images and deployement setup"
	@echo "=============================================="
	@echo ""
	@echo "**Docker Images**
	@echo ""
	@echo "Replace '%' with a stack directory name. The build command will add "
	@echo "the owner name and a tag to the image name (e.g. 'make build/datascience-notebook'"
	@echo "will create make 'illumidesk/datascience-notebook:latest')."
	@echo ""
	@echo ""
	@echo
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build-proxy/%: DARGS?=
build-proxy/%: ## Build and tag a reverse-proxy image
	docker build $(DARGS) --rm --force-rm -t $(ACCOUNT)/$(notdir $@):$(TAG) ./reverse-proxies/$(notdir $@)

build-all-proxies: $(foreach I,$(ALL_PROXY_IMAGES), build-proxy/$(I) ) ## Build all reverse-proxy images

push-proxy/%: ## Push a reverse-proxy image to the registry
	docker push $(ACCOUNT)/$(notdir $@):$(TAG)

push-all-proxies: $(foreach I,$(ALL_PROXY_IMAGES), push-proxy/$(I) ) ## Push all reverse-proxy images

build-app-backend/%: DARGS?=
build-app-backend/%: ## Build and tag a app-backend
	docker build $(DARGS) --rm --force-rm -t $(ACCOUNT)/$(notdir $@):$(TAG) ./$(notdir $@)

build-app-backend: $(foreach I,$(APP-BACKEND_IMAGE), build-app-backend/$(I) ) ## Build app-backend images

push-app-backend/%: ## Push an image to the registry
	docker push $(ACCOUNT)/$(notdir $@):$(TAG)