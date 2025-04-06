#!/bin/bash

set -e

pytest -v --cov=llms4de --cov-report term-missing llms4de "$@"