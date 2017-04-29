#!/usr/bin/env rnaediting

export PATH=$(dirname "$PWD")/src/py/:$PATH

cwl-runner ../src/cwl/rnaediting1strand.cwl workflow_se.1strand.yml