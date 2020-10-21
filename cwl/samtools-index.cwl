#!/usr/bin/env cwl-runner

### doc: "Indexes input alignments and returns alignment with index." ###
### Differs from index.cwl in that index.cwl returns just index ###
### This tool returns alignments with index as secondaryFile    ###

cwlVersion: v1.0

class: CommandLineTool

# hints:
#   - class: DockerRequirement
#     dockerPull: brianyee/samtools:1.6

requirements:
  InitialWorkDirRequirement:
    listing: [ $(inputs.alignments) ]

inputs:
  alignments:
    type: File
    inputBinding:
      position: 2
      valueFrom: $(self.basename)
    label: Input bam file.

baseCommand: [samtools, index, -b]

outputs:
  alignments_with_index:
    type: File
    secondaryFiles: .bai
    outputBinding:
      glob: $(inputs.alignments.basename)


    doc: The index file


$namespaces:
  s: http://schema.org/

$schemas:
- http://schema.org/docs/schema_org_rdfa.html

s:mainEntity:
#   $import: samtools-metadata.yaml

s:downloadUrl: https://github.com/common-workflow-language/workflows/blob/master/tools/samtools-index.cwl
s:codeRepository: https://github.com/common-workflow-language/workflows
s:license: http://www.apache.org/licenses/LICENSE-2.0

s:isPartOf:
  class: s:CreativeWork
  s:name: Common Workflow Language
  s:url: http://commonwl.org/

s:author:
  class: s:Person
  s:name: Andrey Kartashov
  s:email: mailto:Andrey.Kartashov@cchmc.org
  s:sameAs:
  - id: http://orcid.org/0000-0001-9102-5681
  s:worksFor:
  - class: s:Organization
    s:name: Cincinnati Children's Hospital Medical Center
    s:location: 3333 Burnet Ave, Cincinnati, OH 45229-3026
    s:department:
    - class: s:Organization
      s:name: Barski Lab
doc: |
  samtools-index.cwl is developed for CWL consortium

