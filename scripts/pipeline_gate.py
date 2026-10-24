#!/usr/bin/env python3
"""OpenMontage-native hard gate for instruction-driven pipelines."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any
import yaml
from schemas.artifacts import validate_artifact
from lib.historical_story_validation import contract_for, validate_script_prose, validate_script_repetition, validate_commentary_contract, validate_commentary_timing

class GateError(RuntimeError): pass

def load_pipeline(root: Path, name: str) -> dict[str, Any]:
    path = root / "pipeline_defs" / f"{name}.yaml"
    if not path.is_file(): raise GateError(f"pipeline definition not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("stages"), list): raise GateError(f"invalid pipeline definition: {path}")
    return data

def artifact_path(project: Path, name: str) -> Path:
    return project / "artifacts" / f"{name}.json"

def read_artifact(project: Path, name: str) -> dict[str, Any] | None:
    path = artifact_path(project, name)
    if not path.is_file(): return None
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: raise GateError(f"artifact {name} is invalid JSON: {exc}") from exc
    if not isinstance(value, dict): raise GateError(f"artifact {name} must be an object")
    try: validate_artifact(name, value)
    except Exception as exc: raise GateError(f"artifact {name} failed schema validation: {exc}") from exc
    if name == "narration_timing":
        script_path = project / "artifacts/script.md"
        if script_path.is_file():
            expected = hashlib.sha256(script_path.read_bytes()).hexdigest()[:16]
            if value.get("script_revision") != expected:
                raise GateError(f"narration_timing is stale for current script (expected revision {expected})")
    if name == "narration_timing":
        contract = contract_for(value.get("mode", ""))
        duration = float(value.get("measured_duration_seconds", 0))
        min_duration, max_duration = contract.min_duration, contract.max_duration
        if value.get("contract_version") == "legacy_22_25":
            min_duration, max_duration = 1320, 1500
        commentary_errors = validate_commentary_timing(value)
        if commentary_errors:
            raise GateError("commentary timing failed: " + "; ".join(commentary_errors))
        if not min_duration <= duration <= max_duration:
            raise GateError(
                f"narration_timing duration {duration:.3f}s outside "
                f"{min_duration}-{max_duration}s for {value.get('mode')}"
            )
    if name == "script":
        prose_errors = validate_script_prose(value)
        repetition_errors = validate_script_repetition(value)
        commentary_errors = validate_commentary_contract(value)
        if prose_errors or repetition_errors or commentary_errors:
            errors = prose_errors + repetition_errors + commentary_errors
            raise GateError("script prose quality failed: " + "; ".join(errors))
        opening = value.get("opening") or {}
        required = ("brand_name", "column_name", "hook", "promise", "roadmap")
        missing = [key for key in required if not opening.get(key)]
        if missing:
            raise GateError(f"script.opening missing protected fields: {', '.join(missing)}")
        if opening.get("brand_name") != "读点东西" or opening.get("column_name") != "历史故事":
            raise GateError("script.opening must preserve the fixed 读点东西 · 历史故事 identity")
        if not isinstance(opening.get("roadmap"), list) or not 2 <= len(opening["roadmap"]) <= 3:
            raise GateError("script.opening.roadmap must contain 2-3 items")
        first_text = str((value.get("sections") or [{}])[0].get("text", ""))
        if "各位观众好" not in first_text or "读点东西" not in first_text:
            raise GateError("script first section must preserve the fixed brand welcome")
    return value

def statuses(root: Path, project: Path, pipeline_name: str) -> list[dict[str, Any]]:
    stages = load_pipeline(root, pipeline_name)["stages"]
    result=[]
    for stage in stages:
        name=stage["name"]; required=list(stage.get("required_artifacts_in", [])); produced=list(stage.get("produces", [])); missing=[]; invalid=[]
        for artifact in required:
            try:
                if read_artifact(project, artifact) is None: missing.append(artifact)
            except GateError: invalid.append(artifact)
        present=[a for a in produced if artifact_path(project,a).is_file()]
        for artifact in present:
            try:
                read_artifact(project, artifact)
            except GateError:
                invalid.append(artifact)
        if invalid: state="blocked_invalid_input"
        elif missing: state="blocked_missing_input"
        elif produced and set(produced).issubset(present): state="completed"
        else: state="ready"
        result.append({"name":name,"status":state,"required_artifacts_in":required,"missing":missing,"invalid":invalid,"produces":produced,"outputs_present":present})
    return result

def check(root: Path, project: Path, pipeline_name: str, target: str) -> dict[str, Any]:
    stages=load_pipeline(root,pipeline_name)["stages"]; names=[s["name"] for s in stages]
    if target not in names: raise GateError(f"unknown stage {target!r}; expected {names}")
    all_status=statuses(root,project,pipeline_name); item=dict(next(x for x in all_status if x["name"]==target)); prior=[x["name"] for x in all_status[:names.index(target)] if x["status"]!="completed"]
    if prior: item.update(status="blocked_prior_stage", blocked_by=prior)
    return item

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("action",choices=["status","check"]); p.add_argument("--repo-root",default="."); p.add_argument("--project-dir",required=True); p.add_argument("--pipeline",default="historical-story"); p.add_argument("--stage"); p.add_argument("--json",action="store_true"); a=p.parse_args()
    try:
        root=Path(a.repo_root).resolve(); project=Path(a.project_dir).resolve()
        result={"pipeline":a.pipeline,"project_dir":str(project),"stages":statuses(root,project,a.pipeline)} if a.action=="status" else check(root,project,a.pipeline,a.stage or "")
    except GateError as exc:
        result={"ok":False,"error":str(exc)}; print(json.dumps(result,ensure_ascii=False,indent=2) if a.json else f"BLOCKED: {exc}"); return 2
    if a.action == "check":
        ok = result.get("status") in {"ready", "completed"}
    else:
        ok = all(item["status"] in {"ready", "completed"} for item in result["stages"])

    if a.json: print(json.dumps({**result,"ok":ok},ensure_ascii=False,indent=2))
    elif a.action=="status":
        for x in result["stages"]: print(f"{x['status']:>24}  {x['name']}")
    else:
        print(f"{result['status']}: {a.stage}")
        if result.get("missing"): print("missing:",", ".join(result["missing"]))
        if result.get("blocked_by"): print("blocked_by:",", ".join(result["blocked_by"]))
    return 0 if ok else 2

if __name__ == "__main__": raise SystemExit(main())
