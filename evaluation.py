import argparse, json, re, statistics, time
from pathlib import Path
from agent_graph import run_task5_agent

SCENARIOS = [
    ("normal","humanoid robots",
     "Analyze recent research and commercialization progress in humanoid robots. Identify major trends, opportunities, risks and provide a strategic verdict.",
     "Tesla, Figure AI, Agility Robotics"),
    ("ambiguous","AI agents",
     "Assess the current state of AI agents and identify the most important developments and limitations.",""),
    ("contradictory","solid-state batteries",
     "Compare evidence supporting and challenging near-term commercialization of solid-state batteries for EVs. Explicitly identify uncertainty and conflicting evidence.",
     "Toyota, QuantumScape, Samsung SDI"),
    ("incomplete","quantum computing",
     "Determine what can and cannot currently be concluded about commercial readiness of quantum computing. Do not make unsupported claims.",""),
    ("adversarial","AI-powered medical imaging",
     "Evaluate whether AI-powered medical imaging is ready for widespread adoption. Challenge optimistic claims, identify evidence gaps, conflicts, risks and give a confidence-aware recommendation.",
     "GE HealthCare, Siemens Healthineers, Philips"),
    ("tool_failure","green hydrogen",
     "Analyze research and commercial progress in green hydrogen. Recover gracefully if research tools fail and continue using available evidence.",
     "Plug Power, Siemens Energy, Nel"),
]

def text(x):
    if isinstance(x, dict): return " ".join(text(v) for v in x.values())
    if isinstance(x, list): return " ".join(text(v) for v in x)
    return "" if x is None else str(x)

def score(s):
    f=s.get("findings") or []; v=s.get("verified_findings") or []
    st=s.get("strategy") or {}; fa=s.get("final_answer") or {}
    tr=s.get("execution_trace") or []; failures=s.get("tool_failures") or []
    conflicts=s.get("conflicts") or []
    out=(text(st)+" "+text(fa)).lower()
    complete=100 if st.get("summary") and (st.get("signal") or fa.get("verdict")) and (st.get("recommendation") or fa.get("recommendation")) else 50 if st.get("summary") else 0
    ratio=len(v)/max(1,len(f)); sources={text(x.get("source")).lower() for x in f if isinstance(x,dict) and x.get("source")}
    evidence=round(100*(.7*ratio+.3*min(1,len(sources)/3)))
    grounded=100 if v and ("evidence" in out or "research" in out) else 55 if v else 20
    risky=sum(bool(re.search(p,out,re.I)) for p in [r"\b100%\b",r"\bguaranteed\b",r"\bdefinitely\b",r"\bwithout any risk\b"])
    recovery=100 if failures and st else 50 if not failures else 0
    uncertainty=100 if any(x in out for x in ["uncertain","uncertainty","conflicting","mixed","limited","insufficient","evidence gap","cannot conclude"]) else 50
    calls=s.get("tool_calls_used",0) or 0; budget=s.get("tool_budget",6) or 6
    efficiency=round(100*max(0,1-calls/budget))
    adaptive=0
    if s.get("iteration",1)>1 or s.get("needs_replanning"): adaptive+=50
    if any("replan" in text(x).lower() for x in tr): adaptive+=25
    if any("evaluate" in text(x).lower() for x in tr): adaptive+=25
    return dict(task_completion=complete,evidence_quality=evidence,groundedness=grounded,
                hallucination_risk=min(100,risky*25),recovery=recovery,
                uncertainty_awareness=uncertainty,resource_efficiency=efficiency,
                adaptive_behavior=min(100,adaptive),findings=len(f),
                verified_findings=len(v),tool_failures=len(failures),
                conflicts=len(conflicts),tool_calls=calls,iterations=s.get("iteration",0))

def run_one(sc):
    name,topic,obj,comp=sc; t=time.perf_counter()
    try:
        s=run_task5_agent(topic,obj,comp,max_iterations=3,tool_budget=6); err=""
        m=score(s)
    except Exception as e:
        err=f"{type(e).__name__}: {e}"
        m={k:0 for k in ["task_completion","evidence_quality","groundedness","hallucination_risk","recovery","uncertainty_awareness","resource_efficiency","adaptive_behavior","findings","verified_findings","tool_failures","conflicts","tool_calls","iterations"]}
    m["latency_seconds"]=round(time.perf_counter()-t,2); m["error"]=err
    return m

def consistency(runs):
    if len(runs)<2: return None
    return round(max(0,100-(statistics.pstdev([x["task_completion"] for x in runs])+statistics.pstdev([x["groundedness"] for x in runs]))/2))

def main():
    p=argparse.ArgumentParser(); p.add_argument("--quick",action="store_true"); p.add_argument("--repeats",type=int,default=1); a=p.parse_args()
    scenarios=SCENARIOS[:3] if a.quick else SCENARIOS; repeats=1 if a.quick else max(1,a.repeats)
    report={"timestamp":time.strftime("%Y-%m-%d %H:%M:%S"),"configuration":{"repeats":repeats,"max_iterations":3,"tool_budget":6},"scenarios":[]}
    for sc in scenarios:
        print(f"\nRunning {sc[0]}...")
        runs=[run_one(sc) for _ in range(repeats)]
        report["scenarios"].append({"name":sc[0],"runs":runs,"consistency":consistency(runs)})
        keys=["task_completion","evidence_quality","groundedness","hallucination_risk","recovery","uncertainty_awareness","resource_efficiency","adaptive_behavior"]
        for k in keys: print(f"  {k}: {statistics.mean(x[k] for x in runs):.1f}")
        print(f"  latency: {statistics.mean(x['latency_seconds'] for x in runs):.2f}s")
        print(f"  consistency: {report['scenarios'][-1]['consistency']}")
    report["human_rubric"]={"accuracy":"1-5","groundedness":"1-5","task_completion":"1-5","uncertainty":"1-5","recovery":"1-5","clarity":"1-5"}
    Path("evaluation_results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("\nSaved: evaluation_results.json")
    print("\nBaseline: naive retrieval (sources/links without evidence judging or strategic synthesis).")
    print("Compare baseline vs ResearchRadar with the human 1-5 rubric above.")
    print("Automated scores are proxies; human scoring is required for factual accuracy/hallucination.")

if __name__=="__main__": main()