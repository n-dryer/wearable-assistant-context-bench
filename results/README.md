# Sample benchmark results

This directory contains **committed sample output** from running the
v1 benchmark against specific candidate models. It exists so readers
can inspect the report shape — aggregated scoring, per-condition
sensitivity, the reproducibility manifest — without running the
benchmark themselves.

## Directory convention

```
results/
  <ranking_condition>_<model_family>_<model_id_slug>/
    findings.md
```

Examples:

- `results/baseline_claude_sonnet_4_6/findings.md`
- `results/baseline_openai_gpt_4o/findings.md`

The slug is the candidate `model_id` with `.` and `-` collapsed to
`_`. Each directory is a single frozen run against the v1 set under
the ranking condition (`baseline` by default).

## Reproducing a sample

```bash
python experiments/exp_001/run.py \
    --model claude-sonnet-4-6 \
    --output-dir results/baseline_claude_sonnet_4_6/
```

The runner writes `transcripts.jsonl` alongside the findings file.
Transcripts are large and not committed; `findings.md` is the
audit-friendly artifact.

## Current contents

No committed sample runs yet. See [../CHANGELOG.md](../CHANGELOG.md)
for the v1 release note explaining the API-key situation at release
time.
