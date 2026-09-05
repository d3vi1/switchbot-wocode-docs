# How to read protocol evidence

Each claim identifies the component, exact image digest, source location and what the evidence establishes. Four evidence kinds are kept separate:

| Kind | Meaning | Does not establish by itself |
| --- | --- | --- |
| `capture` | Bytes observed during a recorded real interaction | All firmware versions or every possible branch |
| `static` | Behavior traced through instructions in an exact image | Physical actuation, power-loss survival or a complete real-device workflow |
| `hypothesis` | A proposed interpretation with a named resolution condition | An enabled application capability |
| `hardware` | An operation and its postconditions tested on an identified combination | Other hardware revisions or firmware transitions |

Function names are navigation aids, not evidence of semantics. A copied or misleading Ghidra name must be checked against the body and its callers. Equal function addresses across images do not imply equal bytes.

Evidence descriptions distinguish acceptance, RAM mutation, queued downstream work, storage commit and later readback. A status byte or a message-queue call does not prove all of those stages.

Public appendices contain original factual descriptions, addresses, hashes and links. Raw firmware and decompiled vendor code remain outside the CC0 repository. Public fixtures identify whether they are captured or synthetic vectors derived from a static layout.
