# Canonical Authority Evaluation Rule v0.1

## Purpose

This document defines the evaluation criteria for Canonical Authority Review.

The evaluation process is observation-based and does not perform automatic canonical approval.

---

## AuthorityScore

| Score | Meaning                                              |
| ----- | ---------------------------------------------------- |
| 5     | Constitutional or governing source document          |
| 4     | Official architecture or system design document      |
| 3     | Operational policy or implementation design document |
| 2     | Supporting document, diagram, or reference material  |
| 1     | Historical or generated artifact                     |
| 0     | Unknown classification                               |

---

## VersionSignal

| Signal | Meaning                         |
| ------ | ------------------------------- |
| FINAL  | Finalized document indicator    |
| vX.X   | Versioned document indicator    |
| DRAFT  | Draft document indicator        |
| NONE   | No version information detected |

---

## ArtifactType

Allowed classifications:

* Constitution
* Architecture
* Policy
* Evidence
* Diagram
* Asset
* Unknown

---

## HumanGateRelation

Allowed classifications:

* Required
* Related
* Reference
* None
* Unknown

---

## CanonicalStatus

Allowed classifications:

* Candidate
* Supporting
* Historical
* Unknown

---

## Evaluation Principle

This evaluation rule does not perform automatic promotion, deletion, or modification of artifacts.

All final canonical authority decisions require explicit Human Gate approval.

The evaluation output is limited to observation, classification, and evidence-based assessment.
