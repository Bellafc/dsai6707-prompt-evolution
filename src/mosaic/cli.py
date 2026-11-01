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
            out = rp.create(a.task, gpus=gpus, hours=a.hours, gpu_count=a.gpu_count, branch=a.branch,
                            push_branch=a.push_branch, volume_id=a.volume, volume_gb=a.volume_gb, data_center=a.dc,
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

    e3 = sub.add_parser("exp03", help="exp03 data build (Task 2): fetch ground truth, build questions and contexts")
    e3sub = e3.add_subparsers(dest="e3_cmd", required=True)
    e3f = e3sub.add_parser("fetch", help="settled macro markets with daily prices before close (network)")
    e3f.add_argument("--venue", choices=["kalshi", "polymarket"], required=True)
    e3f.add_argument("--since", default="2025-05-01")
    e3sub.add_parser("build", help="question set from the fetched markets: scenario sets, exclusions, counts (offline)")
    e3sub.add_parser("card", help="write research/exp03_data_card.md from the built files (offline)")
    e3sub.add_parser("contexts", help="ALFRED point-in-time panel for every question (network, cached)")
    e3p = e3sub.add_parser("pilot", help="format-compliance pilot on <= 10 calibration questions (GPU)")
    e3p.add_argument("--limit", type=int, default=10)
    e3p.add_argument("--systems", default="base,K',A',M'", help="comma list of base, K, A, M (adapters), K', A', M'")
    e3p.add_argument("--backend", choices=["fake"], default=None)
    e3v = e3sub.add_parser("vintages", help="ALFRED values of one series as of given dates (network, cached)")
    e3v.add_argument("--series", required=True)
    e3v.add_argument("--dates", required=True, help="comma list of YYYY-MM-DD")

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
    pc.add_argument("--gpu", default="80gb", help="80gb | 141gb | 48gb | comma list of RunPod gpuTypeIds")
    pc.add_argument("--gpu-count", type=int, default=1, help="GPUs in the pod (the human must allow more than 1)")
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
    sl = spsub.add_parser("hf-ls", help="list files of a Hugging Face repo (and print its README head)")
    sl.add_argument("repo")
    sa = spsub.add_parser("sae", help="S3: FVU and CE recovered of a Qwen-Scope SAE on public paragraphs")
    sa.add_argument("--model", required=True)
    sa.add_argument("--repo", default="Qwen/SAE-Res-Qwen3-8B-Base-W64K-L0_50")
    sa.add_argument("--layers", default="9,18,27")
    sa.add_argument("--n", type=int, default=200)
    sa.add_argument("--chat", action="store_true")
    sa.add_argument("--tag", required=True)
    sr = spsub.add_parser("adapter-rename", help="copy a PEFT adapter with renamed weight keys")
    sr.add_argument("src")
    sr.add_argument("dst")
    sr.add_argument("--old", default="model.layers.")
    sr.add_argument("--new", default="model.language_model.layers.")
    ss = spsub.add_parser("serve")
    ss.add_argument("--model", default="Qwen/Qwen3-8B")
    ss.add_argument("--adapters-dir", default=None)
    ss.add_argument("--gpu-util", type=float, default=0.90)
    ss.add_argument("--max-batched-tokens", type=int, default=0, help="0 = vLLM default")
    ss.add_argument("--tag", default="S1")

    tr = sub.add_parser("train", help="LoRA SFT of one school adapter (amendment 4 recipe)")
    tr.add_argument("--school", required=True)
    tr.add_argument("--data", required=True, help="jsonl of {messages} or {prompt, response}")
    tr.add_argument("--out", default=None, help="adapter directory (default adapters/<model>/<school>)")
    tr.add_argument("--base", default=None, help="default: [model] base of configs/exp01.toml")
    tr.add_argument("--max-steps", type=int, default=-1, help="smoke tests only")
    tr.add_argument("--bits", type=int, choices=[4, 16], default=16)
    tr.add_argument("--micro-batch", type=int, default=4)

    te = sub.add_parser("teacher", help="generate school SFT trajectories with an open-weight teacher (Change 5)")
    te.add_argument("--n", type=int, required=True, help="trajectories requested per school")
    te.add_argument("--model", default="Qwen/Qwen3.8-Flash-Next-FP8")
    te.add_argument("--tp", type=int, default=1, help="tensor-parallel GPUs for vLLM")
    te.add_argument("--max-model-len", type=int, default=8192)
    te.add_argument("--max-tokens", type=int, default=2048)
    te.add_argument("--no-thinking", action="store_true", help="pass enable_thinking=false to the chat template")
    te.add_argument("--seed", type=int, default=0)
    te.add_argument("--out", default="data/trajectories")
    te.add_argument("--fake", action="store_true", help="offline dry run with the fake backend")

    tx = sub.add_parser("teacher-export", help="teacher requests for a hosted API run by the human (Batch format)")
    tx.add_argument("--n", type=int, required=True, help="trajectories requested per school")
    tx.add_argument("--seed", type=int, default=0)
    tx.add_argument("--model", default="qwen3.8-max", help="model id written into the requests (overridable later)")
    tx.add_argument("--out", required=True, help="jobs directory, e.g. research/teacher_jobs/pilot")
    ti = sub.add_parser("teacher-import", help="validate a hosted-API run and write the training files")
    ti.add_argument("--jobs", required=True, help="jobs directory with manifest.json")
    ti.add_argument("--results", default=None, help="default: <jobs>/results.jsonl")
    ti.add_argument("--out", default="data/trajectories")

    ag = sub.add_parser("agent-spike", help="Qwen3-8B as a framework agent with the real L1/L2 tools (Task A)")
    ag.add_argument("--n", type=int, default=10, help="template events per school")
    ag.add_argument("--seed", type=int, default=7, help="item seed (the teacher's training items use 0)")
    ag.add_argument("--model", default="Qwen/Qwen3-8B")
    ag.add_argument("--thinking", action="store_true", help="thinking mode on (default: enable_thinking=false)")
    ag.add_argument("--max-rounds", type=int, default=4)
    ag.add_argument("--max-tokens", type=int, default=3072)
    ag.add_argument("--out", default="runs/agent-spike")
    ag.add_argument("--fake", action="store_true", help="offline dry run (the fake backend calls no tools)")

    a = ap.parse_args(argv)
    if a.cmd == "agent-spike":
        import json
        import time
        from pathlib import Path

        from mosaic.agent import run_agents, score, spike_jobs
        from mosaic.backends import Cache, FakeBackend, VLLMBackend
        from mosaic.config import ROOT

        sampling = {"temperature": 0.7, "top_p": 0.9, "max_tokens": a.max_tokens, "seed": a.seed}
        if a.fake:
            backend = FakeBackend(sampling)
        else:
            backend = VLLMBackend(sampling, Cache(ROOT / "cache/agent.jsonl"), base_model=a.model, adapters={},
                                  chat_template_kwargs={"enable_thinking": bool(a.thinking)})
        pairs = spike_jobs(a.n, a.seed)
        t0 = time.time()
        run_agents(backend, [j for _, j in pairs], max_rounds=a.max_rounds)
        summary = {"model": a.model, "thinking": bool(a.thinking), "seconds": round(time.time() - t0, 1),
                   **score(pairs)}
        out = Path(a.out) / ("thinking" if a.thinking else "non-thinking")
        out.mkdir(parents=True, exist_ok=True)
        (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
        with (out / "conversations.jsonl").open("w", encoding="utf-8") as f:
            for it, j in pairs:
                f.write(json.dumps({"tag": j.tag, "event": it.event.text, "messages": j.messages, "turns": j.turns},
                                   ensure_ascii=False) + "\n")
        print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
        return 0
    if a.cmd in ("teacher-export", "teacher-import"):
        import json
        from pathlib import Path

        from mosaic import teacher

        if a.cmd == "teacher-export":
            print(f"{teacher.export_jobs(a.n, a.seed, a.model, Path(a.out))} requests written to {a.out}")
        else:
            res = Path(a.results) if a.results else Path(a.jobs) / "results.jsonl"
            print(json.dumps(teacher.import_results(Path(a.jobs), res, Path(a.out)), indent=1))
        return 0
    if a.cmd == "teacher":
        import json
        from pathlib import Path

        from mosaic import teacher
        from mosaic.backends import Cache, FakeBackend, VLLMBackend
        from mosaic.config import ROOT

        cfg = teacher.load_templates()
        items = teacher.make_items(a.n, seed=a.seed, cfg=cfg)
        sampling = {"temperature": 0.8, "top_p": 0.95, "max_tokens": a.max_tokens, "seed": a.seed}
        if a.fake:
            backend = FakeBackend(sampling)
        else:
            backend = VLLMBackend(sampling, Cache(ROOT / "cache/teacher.jsonl"), base_model=a.model, adapters={},
                                  max_model_len=a.max_model_len,
                                  chat_template_kwargs={"enable_thinking": False} if a.no_thinking else None,
                                  engine_kwargs={"tensor_parallel_size": a.tp} if a.tp > 1 else None)
        counts = teacher.generate(backend, items, cfg, "fake" if a.fake else a.model, Path(a.out))
        print(json.dumps({"requested_per_school": a.n, **counts}, indent=1))
        return 0
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
    if a.cmd == "exp03":
        from mosaic import exp03_gt
        if a.e3_cmd == "fetch":
            n = (exp03_gt.fetch_kalshi if a.venue == "kalshi" else exp03_gt.fetch_polymarket)(since=a.since)
            print(f"{a.venue}: {n} new settled markets")
        if a.e3_cmd == "build":
            import json
            from collections import Counter
            from mosaic import exp03_questions as eq
            recs = []
            for f in sorted(exp03_gt.RAW.glob("*_econ.jsonl")):
                recs += [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
            qs, ex = eq.build_events(recs)
            eq.write_jsonl(qs, exp03_gt.RAW.parent / "questions.jsonl")
            eq.write_jsonl(ex, exp03_gt.RAW.parent / "exclusions.jsonl")
            print(f"{len(recs)} markets -> {len(qs)} questions, {len(ex)} exclusions")
            print(json.dumps(eq.counts(qs), indent=1))
            print(Counter(e["reason"] for e in ex).most_common())
        if a.e3_cmd == "card":
            import json
            from mosaic import exp03_questions as eq
            from mosaic.config import ROOT
            d = exp03_gt.RAW.parent
            rd = lambda p: [json.loads(x) for x in p.read_text("utf-8").splitlines() if x.strip()]  # noqa: E731
            n = sum(len(rd(f)) for f in exp03_gt.RAW.glob("*_econ.jsonl"))
            covf = d / "context_coverage.json"
            cov = json.loads(covf.read_text("utf-8")) if covf.exists() else None
            (ROOT / "research/exp03_data_card.md").write_text(
                eq.card(rd(d / "questions.jsonl"), rd(d / "exclusions.jsonl"), n, cov), encoding="utf-8")
            print("wrote research/exp03_data_card.md")
        if a.e3_cmd == "contexts":
            import json
            import sys
            from mosaic import exp03_context as ec
            from mosaic import exp03_questions as eq
            qs = [json.loads(x) for x in (exp03_gt.RAW.parent / "questions.jsonl").read_text("utf-8").splitlines() if x]
            rows = ec.build_contexts(qs, log=sys.stderr)
            eq.write_jsonl(rows, exp03_gt.RAW.parent / "contexts.jsonl")
            cov = ec.coverage(rows)
            (exp03_gt.RAW.parent / "context_coverage.json").write_text(json.dumps(cov, indent=1), encoding="utf-8")
            print(f"{len(rows)} contexts; indicators with < 100% coverage:",
                  {k: v["share"] for k, v in cov.items() if v["share"] < 1})
        if a.e3_cmd == "pilot":
            import json
            from mosaic import exp03_run
            print(json.dumps(exp03_run.pilot(a.systems.split(","), a.limit, a.backend), indent=1))
        if a.e3_cmd == "vintages":
            from mosaic import exp03_context
            for d, v in exp03_context.fetch_asof(a.series, a.dates.split(",")).items():
                print(d, v["vintage"], v["obs"][-4:])
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
