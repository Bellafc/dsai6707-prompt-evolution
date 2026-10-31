"""mosaic <command>: doctor | run | report | judge* | freeze | verify | rescore | status | pod"""

from __future__ import annotations

import argparse
import csv
import sys

from mosaic import locks
from mosaic import run as runmod


def human_gate(exp: str) -> None:
    """Freezing and final test runs are irreversible: they need a person at a terminal (the agent has no tty)."""
    if not sys.stdin.isatty():
        raise SystemExit("this step needs a human at an interactive terminal (program.md, rule 1)")
    if input(f"Type the experiment id ({exp}) to confirm: ").strip() != exp:
        raise SystemExit("not confirmed")


def pod_command(a) -> int:
    import json

    import os

    from mosaic import runpod as rp

    if os.environ.get("RUNPOD_POD_ID") and a.pod_cmd not in ("list", "get") and not getattr(a, "dry_run", False):
        raise SystemExit("pod management runs in the orchestrator session only, not on a pod")
    try:
        if a.pod_cmd == "list":
            for p in rp.list_pods():
                print(rp.summary(p))
        elif a.pod_cmd == "get":
            print(json.dumps(rp.redact(rp.request("GET", f"/pods/{a.pod_id}")), indent=2))
        elif a.pod_cmd in ("stop", "start"):
            rp.request("POST", f"/pods/{a.pod_id}/{a.pod_cmd}")
            print(f"{a.pod_cmd} requested for {a.pod_id}")
        elif a.pod_cmd == "terminate":
            rp.request("DELETE", f"/pods/{a.pod_id}")
            print(f"terminated {a.pod_id} (its pod volume is gone; a network volume stays)")
        elif a.pod_cmd == "create":
            gpus = rp.GPU_CLASSES.get(a.gpu) or [g.strip() for g in a.gpu.split(",") if g.strip()]
            out = rp.create(a.task, gpus=gpus, hours=a.hours, branch=a.branch, push_branch=a.push_branch,
                            volume_id=a.volume, volume_gb=a.volume_gb, data_center=a.dc,
                            image=a.image or rp.DEFAULT_IMAGE, cloud="COMMUNITY" if a.community else "SECURE",
                            with_hf=a.with_hf, jupyter=a.jupyter, template_id=a.template,
                            allow_parallel=a.allow_parallel, dry_run=a.dry_run)
            print(json.dumps(rp.redact(out), indent=2))
        elif a.pod_cmd == "volumes":
            print(json.dumps(rp.request("GET", "/networkvolumes"), indent=2))
        elif a.pod_cmd == "volume-create":
            print(json.dumps(rp.request("POST", "/networkvolumes",
                                        {"name": a.name, "size": a.size, "dataCenterId": a.dc}), indent=2))
    except (rp.RunPodError, ValueError) as e:
        raise SystemExit(str(e)) from None
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mosaic")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", help="check GPU, packages, data and prompts")
    d.add_argument("--arms", default="A,B,C,D")

    r = sub.add_parser("run", help="run arms on a split and log the result")
    r.add_argument("--exp", required=True)
    r.add_argument("--arms", required=True, help="comma list, e.g. A,B,C")
    r.add_argument("--split", choices=["dev", "test"], required=True)
    r.add_argument("--schools", default=None)
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--set", action="append", default=[], dest="overrides", help="dotted override, e.g. arms.B.k=5")
    r.add_argument("--backend", choices=["fake"], default=None)
    r.add_argument("--final", action="store_true")
    r.add_argument("--allow-rerun", default=None)
    r.add_argument("--note", default="")

    rp = sub.add_parser("report", help="paired comparison of the latest run of each arm")
    rp.add_argument("--exp", required=True)
    rp.add_argument("--split", choices=["dev", "test"], required=True)

    f = sub.add_parser("freeze", help="lock prompts, metrics, config and test data before the final run")
    f.add_argument("--exp", required=True)
    v = sub.add_parser("verify", help="check the lock")
    v.add_argument("--exp", required=True)

    rs = sub.add_parser("rescore", help="score saved outputs (e.g. the Confirmation generations) with this harness")
    rs.add_argument("--file", required=True, help="jsonl with a 'text' or 'response' field per line")
    rs.add_argument("--school", required=True)

    pg = sub.add_parser("pregen", help="generate (not score) untuned arms into the cache, e.g. arm D before the freeze")
    pg.add_argument("--exp", required=True)
    pg.add_argument("--arms", required=True)
    pg.add_argument("--split", choices=["dev", "test"], required=True)
    pg.add_argument("--backend", choices=["fake"], default=None)
    pg.add_argument("--note", default="")
    j = sub.add_parser("judge", help="LLM-as-judge on the latest A/B/C runs (exp01 secondary outcome)")
    j.add_argument("--exp", required=True)
    j.add_argument("--split", choices=["dev", "test"], required=True)
    j.add_argument("--limit", type=int, default=None, help="events (dev pilots only)")
    j.add_argument("--backend", choices=["fake"], default=None)
    jr = sub.add_parser("judge-report", help="paired comparisons of judge scores")
    jr.add_argument("--exp", required=True)
    jr.add_argument("--split", choices=["dev", "test"], required=True)
    je = sub.add_parser("judge-export", help="blinded rating sheet for the two human raters")
    je.add_argument("--exp", required=True)
    je.add_argument("--split", choices=["dev", "test"], required=True)
    ja = sub.add_parser("judge-agree", help="human-human and judge-human agreement")
    ja.add_argument("--exp", required=True)
    ja.add_argument("--ratings", required=True, help="comma list of filled rating sheets (CSV)")
    ja.add_argument("--key", default=None)

    sub.add_parser("vendor", help="extract the team's pmpol archive into vendor/")

    st = sub.add_parser("status", help="last rows of experiments/results.tsv")
    st.add_argument("-n", type=int, default=15)

    po = sub.add_parser("pod", help="RunPod pods for the orchestrator (ops/ORCHESTRATOR.md)")
    psub = po.add_subparsers(dest="pod_cmd", required=True)
    psub.add_parser("list", help="all pods: id, name, status, GPU, $/h, push branch")
    for name in ("get", "stop", "start", "terminate"):
        psub.add_parser(name).add_argument("pod_id")
    pc = psub.add_parser("create", help="start one GPU pod for one program.md task")
    pc.add_argument("--task", required=True, help="program.md task id, e.g. S, 0, 1, 2, 5")
    pc.add_argument("--hours", type=float, required=True, help="hard time limit of the agent session (<= 12)")
    pc.add_argument("--gpu", default="80gb", help="80gb | 48gb | comma list of RunPod gpuTypeIds")
    pc.add_argument("--volume", default=None, help="network volume id (persistent /workspace); recommended")
    pc.add_argument("--volume-gb", type=int, default=200, help="pod volume size when no network volume is given")
    pc.add_argument("--dc", default=None, help="data center id (must match the network volume's)")
    pc.add_argument("--branch", default="main", help="branch the pod checks out")
    pc.add_argument("--push-branch", default=None, help="agent/... branch the pod pushes to")
    pc.add_argument("--image", default=None)
    pc.add_argument("--community", action="store_true", help="community cloud instead of secure cloud")
    pc.add_argument("--with-hf", action="store_true", help="also pass the hf_token RunPod secret")
    pc.add_argument("--jupyter", action="store_true", help="start JupyterLab (RunPod secret jupyter_password)")
    pc.add_argument("--template", default=None, help="RunPod template id that carries the secret references")
    pc.add_argument("--allow-parallel", action="store_true")
    pc.add_argument("--dry-run", action="store_true", help="print the request without calling RunPod")
    psub.add_parser("volumes", help="list network volumes")
    pv = psub.add_parser("volume-create", help="create a network volume")
    pv.add_argument("--name", default="mosaic")
    pv.add_argument("--size", type=int, default=200, help="GB")
    pv.add_argument("--dc", required=True, help="data center id, e.g. one that has H100/A100 80GB")

    sp = sub.add_parser("spike", help="Task S spikes on dummy data under scratch/")
    spsub = sp.add_subparsers(dest="spike_cmd", required=True)
    spsub.add_parser("env")
    spsub.add_parser("dummy")
    ss = spsub.add_parser("serve")
    ss.add_argument("--model", default="Qwen/Qwen3-8B")
    ss.add_argument("--adapters-dir", default=None)
    ss.add_argument("--tag", default="S1")

    tr = sub.add_parser("train", help="LoRA SFT of one school adapter (amendment 4 recipe)")
    tr.add_argument("--school", required=True)
    tr.add_argument("--data", required=True, help="jsonl of {messages} or {prompt, response}")
    tr.add_argument("--out", default=None, help="adapter directory (default adapters/<model>/<school>)")
    tr.add_argument("--base", default=None, help="default: [model] base of configs/exp01.toml")
    tr.add_argument("--max-steps", type=int, default=-1, help="smoke tests only")
    tr.add_argument("--bits", type=int, choices=[4, 16], default=16)
    tr.add_argument("--micro-batch", type=int, default=4)

    a = ap.parse_args(argv)
    if a.cmd == "train":
        from mosaic.config import adapters_root, load_toml, paths
        from mosaic.train import train
        mc = load_toml("configs/exp01.toml")["model"]
        out = a.out or str(adapters_root(mc, paths()) / a.school)
        train(base=a.base or mc["base"], data=a.data, out=out, template_kwargs=mc.get("chat_template_kwargs"),
              max_steps=a.max_steps, bits=a.bits, micro_batch=a.micro_batch)
        return 0
    if a.cmd == "spike":
        from mosaic.spikes import main as spike_main
        return spike_main(a)
    if a.cmd == "freeze" or (a.cmd == "run" and (a.final or a.allow_rerun)) or \
            (a.cmd in ("judge", "pregen") and a.split == "test"):
        human_gate(a.exp)
    if a.cmd == "doctor":
        from mosaic.doctor import doctor
        return doctor(a.arms.split(","))
    if a.cmd == "run":
        from mosaic.run import run
        run(a.exp, a.arms.split(","), a.split, schools=a.schools.split(",") if a.schools else None, limit=a.limit,
            overrides=a.overrides, backend=a.backend, final=a.final, allow_rerun=a.allow_rerun, note=a.note)
        return 0
    if a.cmd == "report":
        from mosaic.report import report
        report(a.exp, a.split)
        return 0
    if a.cmd == "freeze":
        lock = locks.freeze(a.exp)
        print(f"frozen {len(lock['files'])} files at {lock['frozen_at']} (commit {lock['commit']}); "
              "commit locks/ now")
        return 0
    if a.cmd == "verify":
        probs = locks.verify(a.exp)
        print("\n".join(probs) or "lock OK")
        return 1 if probs else 0
    if a.cmd == "pregen":
        from mosaic.run import pregen
        if a.split == "test" and a.backend:
            raise SystemExit("no fake backend on the test split")
        pregen(a.exp, a.arms.split(","), a.split, backend=a.backend, note=a.note)
        return 0
    if a.cmd == "judge":
        from mosaic.judge import judge
        if a.split == "test" and (a.limit or a.backend):
            raise SystemExit("judging the test split uses the frozen config: no --limit or fake backend")
        judge(a.exp, a.split, limit=a.limit, backend=a.backend)
        return 0
    if a.cmd == "judge-report":
        from mosaic.judge import judge_report
        judge_report(a.exp, a.split)
        return 0
    if a.cmd == "judge-export":
        from mosaic.judge import judge_export
        judge_export(a.exp, a.split)
        return 0
    if a.cmd == "judge-agree":
        from mosaic.judge import judge_agree
        judge_agree(a.exp, a.ratings.split(","), a.key)
        return 0
    if a.cmd == "vendor":
        from mosaic.vendor import extract
        extract()
        return 0
    if a.cmd == "rescore":
        from mosaic.rescore import rescore
        rescore(a.file, a.school)
        return 0
    if a.cmd == "pod":
        return pod_command(a)
    if a.cmd == "status":
        if not runmod.RESULTS.exists():
            print("no runs yet")
            return 0
        with open(runmod.RESULTS, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
        cols = ["run_id", "status", "consistency_mean", "contamination_mean", "output_rate", "diversity", "note"]
        print("\t".join(cols))
        for row in rows[-a.n:]:
            print("\t".join(str(row.get(c, "")) for c in cols))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
