#!/usr/bin/env rnaediting

export PATH=$(dirname "$PWD")/src/py/:$PATH

cwl-runner ../src/cwl/rnaediting2strands.workflow.cwl workflow_se.2strands.yml