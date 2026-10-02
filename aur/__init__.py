"""
aur: Assessment-Authorization-Runtime enforcement module.

A-U-R theorem: Executable(a,t) <=> Assessment_Admissible(a,t)
               AND Authority_Valid(a,t) AND Runtime_Conformant(a,t)

Modules:
  assessment    - AssessmentRecord creation and admissibility evaluation
  consequence   - ConsequenceRecord (actual consequence, not just execution success)
  enforcement   - single A AND U AND R enforcement point
  reassessment  - Experience Memory -> Assessment context bridge
"""
