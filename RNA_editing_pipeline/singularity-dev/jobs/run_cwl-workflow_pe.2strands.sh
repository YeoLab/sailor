#!/usr/bin/env rnaediting

export PATH=$(dirname "$PWD")/src/py/:$PATH

cwl-runner --jobStore ./tmp ../src/cwl/rnaediting2strands.workflow.cwl example-pe.yml
