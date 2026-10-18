from pathlib import Path
p=Path("src/ppiblocker/pipeline.py")
s=p.read_text()
old='    gates=data.get("gates",{})'
new='''    mode=data.get("structure",{}).get("mode","retrieve")
    require(mode in {"retrieve","predict_only"},"INVALID_STRUCTURE_MODE","Use retrieve or predict_only")
    if mode=="predict_only":
        require(not any(k in data.get("structure",{}) for k in ("pdb","path","assembly","chains","provenance","experimental")),
                "BLIND_STRUCTURE_LEAKAGE","predict_only cannot carry reference coordinates or identity hints")
        require(not any(k in data.get("prediction",{}) for k in ("templates","template","constraints","contacts")),
                "BLIND_STRUCTURE_LEAKAGE","No templates or interface constraints in blind native-pose prediction")
    gates=data.get("gates",{})'''
assert s.count(old)==1
s=s.replace(old,new)
old='''        spec=config.get("structure",{})
        failed=[];accepted=None'''
new='''        spec=config.get("structure",{})
        if spec.get("mode")=="predict_only":
            put(run,"retrieval",{"receipts":repo.receipts,"rejected":[],"search_performed":False,
                                "reason":"explicit_blind_prediction","experimental_coordinates_accessed":False})
            return run.finish("NEEDS_PREDICTION","blind_pose_input",
                              {"next_step":"predict","benchmark_track":"sequence_only",
                               "training_leakage_status":"unknown"})
        failed=[];accepted=None'''
assert old in s
p.write_text(s.replace(old,new))
p=Path("src/ppiblocker/common.py");s=p.read_text()
start=s.index("def checked_command(");end=s.index("\ndef source_provenance",start)
new='''def checked_command(argv, directory, log, env=None, timeout=86400):
    """Durable command and resource receipt, including failed/timeout invocations."""
    import time
    directory, log = Path(directory), Path(log)
    directory.mkdir(parents=True, exist_ok=True);log.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(log.with_suffix(".command.json"), {"argv": list(map(str,argv)), "cwd":str(directory)})
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt={"started_utc":datetime.now(timezone.utc).isoformat(),"timeout_seconds":timeout,
             "slurm_job_id":os.environ.get("SLURM_JOB_ID"),"allocated_gpus":os.environ.get("SLURM_GPUS_ON_NODE"),
             "status":"RUNNING","returncode":None}
    started=time.monotonic()
    try:
        with log.open("w") as f:
            result=subprocess.run(list(map(str,argv)),cwd=directory,env=env,stdout=f,
                                  stderr=subprocess.STDOUT,timeout=timeout,check=False)
        receipt.update(returncode=result.returncode,status="COMPLETE" if result.returncode==0 else "FAILED")
        require(result.returncode==0,"BACKEND_FAILED",f"Exit {result.returncode}; log={log}")
    except (OSError,subprocess.TimeoutExpired) as error:
        receipt.update(status="TIMEOUT" if isinstance(error,subprocess.TimeoutExpired) else "LAUNCH_FAILED",error=str(error))
        raise EvidenceError("BACKEND_FAILED",f"{error}; log={log}") from error
    finally:
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt.update(wall_seconds=time.monotonic()-started,
                       child_user_cpu_seconds=after.ru_utime-before.ru_utime,
                       child_system_cpu_seconds=after.ru_stime-before.ru_stime,
                       child_maxrss_process_highwater_kb=after.ru_maxrss,
                       maxrss_semantics="process child high-water mark, not isolated per command",
                       gpu_utilization_measured=False,ended_utc=datetime.now(timezone.utc).isoformat())
        atomic_json(log.with_suffix(".resources.json"),receipt)
    return record_file(log)
'''
p.write_text(s[:start]+new+s[end:])

