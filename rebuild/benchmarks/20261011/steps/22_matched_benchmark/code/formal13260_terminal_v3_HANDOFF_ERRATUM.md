# Readonly V3 handoff erratum
The sentence “first CPU hashes and32 software contracts” in formal13260_terminal_v3/HANDOFF.md is a documentation typo. Actual readonly source enforces suite.countTestCases()==34. The34 contracts comprise32 existing gates plus2 scientific-input/source readonly distinction contracts. Independent static review PASS, CPU tests/hash NOT_EXECUTED_RESOURCE_UNAVAILABLE. No source/parameters/eligibility/protocol changes and no source file mutated.
Use only formal13260_terminal_v3/formal13260_terminal_cpu.sbatch with --dependency=afterany:13260. V1/V2 are unexecuted history. Root owns submission.

