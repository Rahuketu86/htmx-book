.ONESHELL:
SHELL := /bin/bash

ENV := $(PWD)/.env

# Environment variables for project
include $(ENV)

# Export all variable to sub-make
export

dockerimg:
	docker build -t htmxapp .

runapp:
	docker run -p 5000:5000 -it htmxapp

deploy-space:
	git push --force space main
