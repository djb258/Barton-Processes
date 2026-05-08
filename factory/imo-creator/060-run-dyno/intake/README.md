# FCE Intake — Process-Local Pointer

**This directory is a process-local pointer only.**

Canonical FCE intake template, fill instructions, and worked examples live in:

```
imo-creator-v2/atlas/fce-intake/
├── template.yaml          ← copy + fill this
├── FILL_INSTRUCTIONS.md   ← your only doc as an operator
└── examples/
    ├── insurance-underwriting.yaml
    └── storage-go-no-go.yaml
```

**Authority:** `imo-creator-v2` (atlas). All edits to the template and instructions go there.

**Operator workflow:** Copy `template.yaml`, fill per `FILL_INSTRUCTIONS.md`, drop filled file into `atlas/dyno/planner-queue/processing/`. Read `FCE_DESCRIPTION_GUIDANCE.md` before writing your domain description.

Do not maintain a parallel copy of the template here. Consume from the atlas canonical location.
