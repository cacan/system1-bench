# Benchmark fixtures

Fixtures are JSON Lines. Each line is a case with:

- `id`: stable case identifier;
- `state`: text/object/array presented to the provider;
- `questions`: one or more typed decisions;
- `labels`: optional expected answers used for evaluation.

Question types:

- `noul`: binary decision; label is a JSON boolean.
- `choice`: finite named options; criteria is an object mapping option names to descriptions; label is an option name.
- `score`: ordered levels; criteria is a list of at least two levels; label is a zero-based integer.

The smoke fixture is intentionally small. Keep public benchmark data and private/customer data in separate files, and do not ingest private data into Qdrant without an explicit source policy.
