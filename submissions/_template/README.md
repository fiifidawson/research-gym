# The shape of a submissions folder

Copy this layout, replacing `_template` with your GitHub handle:

```
submissions/your-handle/
  00-onboarding/profile.json   ← start here
  01-oop-refresher/nn.py
```

One directory per module, named exactly like the one under `modules/`, containing exactly the file
the module's `TASK.md` asks for. The check looks it up by name, so `nn.py` cannot be `NN.py` or
`nn_solution.py`.

Anything else you put in your folder — notes, a scratch script, a plot — is yours and is ignored by
the checks.
