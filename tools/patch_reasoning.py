import os, sys
import crewai
from crewai import LLM

_orig_init = LLM.__init__
def _patched_init(self, *a, **kw):
    ap = dict(kw.pop("additional_params", None) or {})
    ap.setdefault("reasoning_effort", "high")
    kw["additional_params"] = ap
    return _orig_init(self, *a, **kw)
LLM.__init__ = _patched_init
print("[patch] reasoning_effort=high injected", flush=True)
