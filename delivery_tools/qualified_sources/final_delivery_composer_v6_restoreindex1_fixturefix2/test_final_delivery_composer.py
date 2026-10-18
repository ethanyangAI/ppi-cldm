"""PureCPU boundaries and real accepted resolver/statistics APIs. No production models."""
import copy,json,tempfile,unittest
from pathlib import Path
import final_delivery_composer as m
def request(mode="inventory"):
    return dict(schema="final-delivery-"+mode+"-request.v1",root_owned=True,formal_array_job_id="13260",scientific_scope="COMPUTATIONAL_ONLY")
class Contracts(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(dir=m.R/"steps/24_benchmark_delivery/tmp",prefix="composer_fixture_");self.d=Path(self.t.name)
    def tearDown(self):self.t.cleanup()
    def file(self,name="input.txt",data=b"fixture",readonly=False):
        p=self.d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        if readonly:p.chmod(0o444)
        return m.rec(p)
    def alias(self,original,archived):
        return dict(original=original,archived=archived,status="READONLY_BYTE_IDENTICAL_ALIAS")
    def test_01_explicit_root_inventory(self):m.request(request(),"inventory")
    def test_02_wrong_schema(self):
        q=request();q["schema"]="loose"
        with self.assertRaises(ValueError):m.request(q,"inventory")
    def test_03_unowned_request(self):
        q=request();q["root_owned"]=False
        with self.assertRaises(ValueError):m.request(q,"inventory")
    def test_04_other_formal_array(self):
        q=request();q["formal_array_job_id"]="1"
        with self.assertRaises(ValueError):m.request(q,"inventory")
    def test_05_experimental_scope(self):
        q=request();q["scientific_scope"]="EXPERIMENTAL"
        with self.assertRaises(ValueError):m.request(q,"inventory")
    def test_06_zero_length_receipt(self):self.assertEqual(m.shape(self.file(data=b""))["bytes"],0)
    def test_07_bool_byte_count_rejected(self):
        r=self.file();r["bytes"]=True
        with self.assertRaises(ValueError):m.shape(r)
    def test_08_wrong_sha_shape(self):
        r=self.file();r["sha256"]="nearest"
        with self.assertRaises(ValueError):m.shape(r)
    def test_09_outside_authority(self):
        with self.assertRaises(ValueError):m.safe("/tmp/outside")
    def test_10_readonly_verified(self):m.verify(self.file(readonly=True),True)
    def test_11_changed_bytes_rejected(self):
        r=self.file();Path(r["path"]).write_bytes(b"changed")
        with self.assertRaises(ValueError):m.verify(r)
    def test_12_symbolic_path_rejected(self):
        r=self.file();p=self.d/"link";p.symlink_to(r["path"])
        with self.assertRaises(ValueError):m.safe(p)
    def test_13_private_filename_rejected(self):
        r=self.file(".env")
        with self.assertRaises(ValueError):m.scan(r["path"])
    def test_14_literal_credential_rejected(self):
        r=self.file(data=b"api_"+b"key="+b"a"*20)
        with self.assertRaises(ValueError):m.scan(r["path"])
    def test_15_chunk_boundary_credential_rejected(self):
        r=self.file(data=b"."*(1048576-5)+b"api_"+b"key="+b"a"*20)
        with self.assertRaises(ValueError):m.scan(r["path"])
    def test_16_complete_normal_raw_file(self):m.scan(self.file(data=b"\x00raw\n")["path"])
    def test_17_env_conditional(self):self.assertTrue(m.conditional(m.R/"env/core/bin/python"))
    def test_18_weights_conditional(self):self.assertTrue(m.conditional(self.d/"weights/model.bin"))
    def test_19_raw_confidence_not_conditional(self):self.assertFalse(m.conditional(self.d/"raw/pae_model.npz"))
    def test_20_alias_byte_change_rejected(self):
        a=self.file("a",b"old",True);b=self.file("b",b"new",True)
        with self.assertRaises(ValueError):m.merge_alias([self.alias(a,b)],{})
    def test_21_alias_status_rejected(self):
        a=self.file(readonly=True);e=self.alias(a,a);e["status"]="RECONSTRUCTED"
        with self.assertRaises(ValueError):m.merge_alias([e],{})
    def test_22_writable_alias_rejected(self):
        a=self.file()
        with self.assertRaises(ValueError):m.merge_alias([self.alias(a,a)],{})
    def test_23_equal_alias_deterministic(self):
        a=self.file("z",b"same",True);b=self.file("a",b"same",True);logical=dict(a,path=str(self.d/"original"));rows={}
        m.merge_alias([self.alias(logical,a),self.alias(logical,b)],rows)
        self.assertEqual(rows[m.key(logical)]["archived"],b)
    def test_24_old_revisions_need_exact_sha(self):
        a=self.file("a",b"old",True);b=self.file("b",b"new",True);rows={};logical=str(self.d/"original")
        m.merge_alias([self.alias(dict(a,path=logical),a),self.alias(dict(b,path=logical),b)],rows)
        self.assertEqual(len(rows),2)
    def test_25_real_restore_reads_only_restored_alias(self):
        a=self.file("old.py",b"original");old=Path(a["path"]);old.unlink()
        archived=self.file("archive.py",b"original",True);e=self.alias(a,archived);restore=self.d/"restore"
        dest=restore/Path(archived["path"]).relative_to(m.R);dest.parent.mkdir(parents=True);dest.write_bytes(b"original");dest.chmod(0o444)
        lib=m.load("composer_fixture_restore",m.LIB/"restore_resolver_v2.py");P=lib.path_factory(m.R,restore,dict(aliases=[e]))
        self.assertEqual(P(a["path"],expected_sha=a["sha256"]).physical(),dest)
        self.assertFalse(old.exists())
    def test_26_unknown_history_rejected_real_API(self):
        al=m.load("composer_fixture_aliases",m.LIB/"provenance_aliases_v2.py");hl=m.load("composer_fixture_history",m.LIB/"historical_scope_v2.py")
        rr=self.file();e=dict(status="HISTORICAL_UNRESOLVED_PROVENANCE",current_PASS_allowed=False,original=rr)
        resolver=al.ReceiptResolver(m.R,index=dict(historical_unresolved=[e]))
        with self.assertRaises(ValueError):hl.HistoricalScopeVerifier(resolver).metadata(e)
    def test_27_existing_gate_actual_status(self):
        r=self.file(data=json.dumps(dict(status="ACTUAL",models=74)).encode())
        self.assertEqual(m.expect(r,dict(status="ACTUAL",models=74))["models"],74)
    def test_28_gate_pending_not_acceptance(self):
        r=self.file(data=json.dumps(dict(status="PENDING")).encode())
        with self.assertRaises(ValueError):m.expect(r,dict(status="ACCEPTED"))
    def test_29_restore_API_config_shape(self):
        raw=self.file("sacct.txt");account=self.file("account.json",json.dumps(dict(raw_sacct=raw)).encode());plan=self.file("plan.json",b"{}");run=self.file("runs.json",b"[]");co=self.file("cohorts.json",b"{}");audit=self.file("audit.py");summary=self.file("statistics.json",b"{}")
        col=dict(schema="formal_postprocess_collection.v2",status="FORMAL_ALLOCATION_NATIVE_AND_COHORT_CLOSURE_ACCEPTED",plan=plan,sources=dict(independent=audit),files=dict(accounting=account,run_receipts=run,cohorts=co))
        cfg={"result":"exact.json"};r=m.recomputation(col,cfg,summary)
        self.assertEqual(set(r["generation"]),{"auditor_source","plan","run_receipts","sacct","producer_accounting","producer_cohort"})
        self.assertEqual(r["common"],cfg);self.assertEqual(r["statistics"]["producer_summary"],summary["path"])
    def test_30_real_statistics112_empty_all6_null(self):
        lib=m.load("composer_fixture_statistics",m.LIB/"target_statistics_v2.py")
        p=dict(protocol_id="FIXTURE",targets=[dict(target_id="T"+str(i),analysis_role="primary"if i<6 else"diagnostic")for i in range(7)],methods=[dict(method_id=x)for x in("rf_diffusion","bindcraft")],replicate_seeds=[21011,21012],budget_gpu_seconds=3600,sampling=dict(uniform_n_per_replicate=3,native_top_k_per_replicate=2))
        tasks=lib.expected_tasks(p);plan=dict(status="FROZEN_BEFORE_GENERATION",protocol=p,tasks=tasks)
        cov=[dict(task=t,uniform_all_complete=dict(requested=3,selected=0,underfilled=True),native_fixed_top_k=dict(requested=2,selected=0,underfilled=True))for t in tasks]
        r=lib.statistics(dict(cohort_summaries=[]),plan,dict(coverage=cov,selected=[]),"rf_diffusion","bindcraft")
        self.assertEqual((r["n_cohort_engine_rows"],len(r["rows"])),(112,56))
        self.assertTrue(all(v["paired_macro_mean_RF_minus_BindCraft"]is None for v in r["comparisons"]))

    def test_31_inventory_added_file_rejected(self):
        r=self.file();io=dict(files=[dict(receipt=r,scope_root=str(self.d))],conditional_inference_dependencies=[])
        self.file("unbound.log")
        with self.assertRaises(ValueError):m.inventory_universe(io)
    def test_32_inventory_missing_file_rejected(self):
        r=self.file();Path(r["path"]).unlink();io=dict(files=[dict(receipt=r,scope_root=str(self.d))],conditional_inference_dependencies=[])
        with self.assertRaises(ValueError):m.inventory_universe(io)
    def test_33_inventory_exact_all_files(self):
        a=self.file("run.log");b=self.file("raw.pdb");io=dict(files=[dict(receipt=r,scope_root=str(self.d))for r in(a,b)],conditional_inference_dependencies=[])
        self.assertEqual(m.inventory_universe(io),{a["path"],b["path"]})

# These ten fixtures call actual frozen APIs with explicitly synthetic content.
# Synthetic helper constants are changed only in a separately named test module.
from unittest import mock
import relative_archive_restore as wrapper
class ExactContextContracts(unittest.TestCase):
    setUp=Contracts.setUp
    tearDown=Contracts.tearDown
    file=Contracts.file
    alias=Contracts.alias
    def toy(self,unknown=False):
        ctx=m.load("synthetic_composer_context_"+self.d.name,m.context_template())
        ctx.ROOT=self.d/"synthetic_bbf13226";ctx.ROOT.mkdir()
        names=("metrics.json","model_crosschecks.json","cases.tsv","paired_changes.tsv","original_labels.tsv","REPORT_ZH.md")
        children=[]
        for i,n in enumerate(names):children.append(self.file("synthetic_bbf13226/runs/review_13226/"+n,(json.dumps(dict(synthetic=i))if n.endswith(".json")else"synthetic\n").encode()))
        ctx.ROWS=tuple((Path(r["path"]).name,r["bytes"],r["sha256"])for r in children)
        obj=dict(job_id="13226",status="BBF110_INDEPENDENT_DEVELOPMENT_DIAGNOSIS_CONTENT_ACCEPTED",fixture_not_scientific_evidence=True,outputs=[dict(r,path="runs/review_13226/"+n)for r,n in zip(children,names)])
        if unknown:obj["unapproved"]={"path":"runs/unapproved.txt","bytes":1,"sha256":"0"*64}
        parent=self.file("synthetic_bbf13226/runs/review_13226/manifest.json",json.dumps(obj).encode());ctx.PARENT=parent
        mapping=dict(schema=ctx.SCHEMA,status=ctx.STATUS,parent_manifest=parent,declared_relative_root=str(ctx.ROOT),entries=[ctx.expected_entry(i)for i in range(6)],original_json_unchanged=True,parent_and_all_six_child_bytes_verified=True)
        mr=m.dump(self.d/"synthetic_mapping.json",mapping)
        return ctx,mr,parent,children
    def config(self,parent,children,mapping):
        sources=[]
        for name in("phase.json","reconstruction.json","human.txt"):sources.append(self.file(name,b"{}"))
        previous=self.file("ACTIVE.json",json.dumps(dict(zip(("current_phase","reconstruction","human_report"),sources))).encode())
        inclusion=self.file("inclusion.json",json.dumps(dict(status="SOURCE_INCLUSION_AUDIT_PASS",files=[])).encode())
        gates={}
        files=[previous,inclusion,parent,mapping]+children+sources
        for name in m.GATES:
            obj=dict(status="SYNTHETIC_SOFTWARE_FIXTURE")
            if name=="generation_accounting":obj.update(complete_generation_matrix=True,expected_tasks=28)
            if name=="common_review_content":obj.update(status="COMMON_REVIEW_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY",independent_experimental_validation=False)
            if name=="source_release":obj.update(working_tree_clean=True,commit="a"*40,source_inclusion=inclusion)
            r=self.file("gate_"+name+".json",json.dumps(obj).encode());files.append(r)
            gates[name]=dict(receipt=r,expect=dict(status=obj["status"]))
        aliases=self.file("aliases.json",json.dumps(dict(aliases=[],historical_unresolved=[])).encode());files.append(aliases)
        config=dict(schema="benchmark-delivery.v2",scientific_scope="COMPUTATIONAL_ONLY",authority_root=str(m.R),phase_id="SYNTHETIC_SOFTWARE_FIXTURE",previous_active=previous,gates=gates,resource_aliases=aliases,files=[dict(receipt=r,classification="EVIDENCE")for r in files],conditional_inference_dependencies=[])
        return self.file("config.json",json.dumps(config).encode())
    def git_fixture(self,api):
        original=api.subprocess.check_output
        def call(argv,*args,**kwargs):
            if argv[0]=="git":return"a"*40+"\n"if"rev-parse"in argv else""
            return original(argv,*args,**kwargs)
        return mock.patch.object(api.subprocess,"check_output",side_effect=call)
    def test_34_exact_parent_six_edge_read_view(self):
        ctx,mr,parent,children=self.toy();mapping=json.loads(Path(mr["path"]).read_text())
        for i,child in enumerate(children):
            r=json.loads(Path(parent["path"]).read_text())["outputs"][i]
            canonical,proof=ctx.normalize_edge(r,parent,("outputs",str(i)),mapping)
            self.assertEqual(canonical,child);self.assertNotIn("original_receipt",proof)
        with self.assertRaises(ValueError):ctx.normalize_edge(r,parent,("other",str(i)),mapping)
    def test_35_actual_frozen_validate_exact_context_and_original_bytes(self):
        ctx,mr,parent,children=self.toy();config=self.config(parent,children,mr);api=m.load("synthetic_core_context_pass",m.LIB/"delivery_core_v2.py");original=api.read
        reader=ctx.VerifiedContextReader(mr,api.read)
        with self.git_fixture(api):
            result,proof=m.validate_archive_context(api,config["path"],str(self.d/"validation.json"),reader,dict(synthetic_fixture=True))
        self.assertEqual(result["status"],"FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY")
        self.assertIs(api.read,original);self.assertEqual(m.rec(parent["path"]),parent)
        self.assertEqual(len(reader.used),1);self.assertTrue(Path(proof["path"]).is_file())
    def test_36_actual_frozen_validate_without_context_rejects_relative(self):
        ctx,mr,parent,children=self.toy();config=self.config(parent,children,mr);api=m.load("synthetic_core_context_missing",m.LIB/"delivery_core_v2.py")
        with self.git_fixture(api),self.assertRaisesRegex(ValueError,"OUTSIDE_AUTHORITY_RECEIPT"):
            api.validate(config["path"],str(self.d/"validation.json"))
    def test_37_unknown_relative_still_rejected_and_reader_restored(self):
        ctx,mr,parent,children=self.toy(unknown=True);config=self.config(parent,children,mr);api=m.load("synthetic_core_context_unknown",m.LIB/"delivery_core_v2.py");original=api.read
        reader=ctx.VerifiedContextReader(mr,api.read)
        with self.git_fixture(api),self.assertRaisesRegex(ValueError,"OUTSIDE_AUTHORITY_RECEIPT"):
            m.validate_archive_context(api,config["path"],str(self.d/"validation.json"),reader,dict(synthetic_fixture=True))
        self.assertIs(api.read,original);self.assertFalse((self.d/"validation_context.json").exists())
    def restore_fixture(self):
        ctx,mr,parent,children=self.toy();root=self.d/"restored";root.mkdir();index=[]
        for i,r in enumerate([mr,parent]+children):
            p=root/("evidence/"+str(i));p.parent.mkdir(exist_ok=True);p.write_bytes(Path(r["path"]).read_bytes());p.chmod(0o444)
            index.append(dict(logical=r,restored_relative=p.relative_to(root).as_posix()))
        return ctx,mr,parent,children,root,index
    def test_38_restored_mapping_works_without_any_live_original(self):
        ctx,mr,parent,children,root,index=self.restore_fixture()
        for r in [mr,parent]+children:Path(r["path"]).unlink()
        mapping,proof=ctx.verify_restored_mapping(mr,str(root),index)
        self.assertTrue(proof["all_read_paths_under_restored_root"]);self.assertTrue(proof["no_live_root_fallback"])
        self.assertEqual(len(proof["children_restored_paths"]),6)
    def test_39_missing_restored_child_rejected_despite_live_file(self):
        ctx,mr,parent,children,root,index=self.restore_fixture()
        (root/index[-1]["restored_relative"]).unlink()
        self.assertTrue(Path(children[-1]["path"]).exists())
        with self.assertRaises(ValueError):ctx.verify_restored_mapping(mr,str(root),index)
    def test_40_mapper_actual_CPU_terminal_record_not_software_label(self):
        r=dict(path=str(self.d/"receipt.json"),bytes=0,sha256="0"*64)
        accepted=dict(allocation=dict(job_id="9"),source_files=[],contracts=r,mapping_verification=r,read_view_proof=r)
        prerequisite=dict(mapper_acceptance=r,source_files=[],contracts=r,mapping_verification=r,read_view_proof=r,actual_terminal_accounting=dict(row=["9","COMPLETED","0:0","2","cpu=1,mem=16G","u21111210118","u21111210118","test9_exact_context_v4","organ"],allocated_GPUs=0))
        prerequisite["actual_terminal_accounting"]["raw"]="|".join(prerequisite["actual_terminal_accounting"]["row"])+"|\n"
        binding=dict(mapper_acceptance=r,actual_mapper_prerequisite=prerequisite)
        wrapper.mapper_terminal_shape(binding,accepted)
        prerequisite["actual_terminal_accounting"]["row"][4]+=",gres/gpu=1"
        with self.assertRaises(ValueError):wrapper.mapper_terminal_shape(binding,accepted)
    def test_41_executed_helper_drift_rejected_in_current_binding(self):
        api=m.context_api();pins=m.sources()["context_API_dependencies"];changed=[dict(r)for r in pins];changed[0]["sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"differs"):api.executed_mapper_binding(changed,pins,m.identity)

    def source_fixture(self):
        own=self.file("executed_composer.py",b"synthetic composer",True);dep=self.file("executed_library.py",b"synthetic library",True)
        def actual():return dict(composer=[m.rec(own["path"])],existing_API_dependencies=[m.rec(dep["path"])])
        return own,dep,actual
    def test_42_executing_composer_byte_drift_rejected(self):
        own,dep,actual=self.source_fixture();accepted=actual()
        with mock.patch.object(m,"sources",side_effect=actual):wrapper.executing_source_binding(accepted)
        p=Path(own["path"]);p.chmod(0o644);p.write_bytes(b"changed composer");p.chmod(0o444)
        with mock.patch.object(m,"sources",side_effect=actual),self.assertRaisesRegex(ValueError,"Whole executing"):wrapper.executing_source_binding(accepted)
    def test_43_executing_library_byte_drift_rejected(self):
        own,dep,actual=self.source_fixture();accepted=actual()
        p=Path(dep["path"]);p.chmod(0o644);p.write_bytes(b"changed library");p.chmod(0o444)
        with mock.patch.object(m,"sources",side_effect=actual),self.assertRaisesRegex(ValueError,"Whole executing"):wrapper.executing_source_binding(accepted)

class ThreeContextComposerContracts(unittest.TestCase):
    setUp=Contracts.setUp
    tearDown=Contracts.tearDown
    file=Contracts.file
    toy=ExactContextContracts.toy
    config=ExactContextContracts.config
    git_fixture=ExactContextContracts.git_fixture
    def three(self,unknown=False):
        old,mr,parent,children=self.toy();bundle=m.context_api().load_bundle();b,h,f=bundle.b,bundle.h,bundle.f
        b.PARENT=old.PARENT;b.ROOT=old.ROOT;b.ROWS=old.ROWS
        # Constants are overridden only in this isolated fixture module instance.
        raw=dict(entries=[dict(sequence="SYNTHETIC_"+str(i))for i in range(3)],recovery=copy.deepcopy(h.RECOVERY_MARKER),other=dict(keep=True))
        for row in h.ROWS:raw["entries"][int(row["source_field"][1])][row["source_field"][2]]=h.logical(row)
        if unknown:raw["unknown_current"]={"path":"/UNAPPROVED/current.pdb","bytes":1,"sha256":"0"*64}
        h.PARENT=self.file("recovery/recovered_three_candidates.json",json.dumps(raw).encode(),True)
        five=[]
        for i,(name,_,_)in enumerate(f.ROWS):
            if name=="recovered_three_candidates.json":r=h.PARENT
            else:
                # JSON evidence must be valid JSON; TXT evidence stays literal text.
                payload=json.dumps(dict(SYNTHETIC_SOFTWARE_ONLY=True,evidence_name=name,evidence_index=i)).encode()if Path(name).suffix==".json"else("SYNTHETIC_EVIDENCE_"+str(i)).encode()
                r=self.file("recovery/"+name,payload,True)
            five.append(r)
        f.ROWS=[(Path(r["path"]).name,r["bytes"],r["sha256"])for r in five]
        fraw=dict(schema_version=1,session_id=f.SESSION,recovery_type=f.RECOVERY_TYPE,files=[dict(path=n,bytes=size,sha256=sha)for n,size,sha in f.ROWS],records=[{"keep":"ORIGINAL_TOY_PAYLOAD"}])
        f.PARENT=self.file("recovery/candidate_recovery_receipt.json",json.dumps(fraw).encode(),True)
        lineage=[self.file("lineage/"+str(i)+".json",b"{}",True)for i in range(6)]
        hm=dict(schema=h.SCHEMA,status=h.STATUS,parent_manifest=h.PARENT,recovery_marker=h.RECOVERY_MARKER,recovery_status=h.RECOVERY_MARKER["status"],recovery_missing_files=h.RECOVERY_MARKER["missing_files"],entries=[h.expected_entry(i)for i in range(9)],anchor={**h.ROWS[8],"canonical_receipt":None,"historical_file_restored":False,"status":h.ANNOTATION_STATUS},historical_annotation_n=9,canonical_external_text_edge_n=0,unresolved_current_external_edges_allowed=False,original_json_unchanged=True,external_files_read=False,current_declared_graph_only=True,raw_byte_acceptance=False,actual_current_sequence_input_parent_bytes_verified=True,accepted_lineage_receipts=lineage,producer_executed_source=lineage[0],producer_actual_software_gate=lineage[1],source_graph_selector=lineage[2],prior_accepted_inclusion=lineage[3])
        fm=dict(schema=f.SCHEMA,status=f.STATUS,parent_manifest=f.PARENT,session_id=f.SESSION,recovery_type=f.RECOVERY_TYPE,entries=[f.expected_entry(i)for i in range(5)],current_recovered_evidence_file_n=5,all_five_current_files_independently_verified=True,all_five_relative_edges_observed=True,original_json_unchanged=True,external_files_read=False,unknown_relative_edges_allowed=False,raw_byte_acceptance=True,new_scientific_inference=False,old_structures_backbones_or_MD_restored=False,current_declared_graph_only=True,accepted_lineage_receipts=lineage[:4],producer_executed_source=lineage[0],producer_actual_software_gate=lineage[1],source_graph_selector=lineage[2],prior_accepted_inclusion=lineage[3])
        hr=m.dump(self.d/"history_mapping.json",hm);fr=m.dump(self.d/"five_mapping.json",fm)
        config=self.config(parent,children,mr);obj=m.read(config["path"]);obj["files"] += [dict(receipt=r,classification="EVIDENCE")for r in [f.PARENT,hr,fr,*five,*lineage]]
        # Historical parent is already the fourth real recovered child; archive it once.
        if five[3]!=h.PARENT:raise ValueError("Shared synthetic historical parent identity differs")
        config=m.dump(self.d/"three_config.json",obj)
        parents={parent["path"]:(b,json.loads(Path(mr["path"]).read_text())),h.PARENT["path"]:(h,hm),f.PARENT["path"]:(f,fm)}
        class SyntheticExactThreeReader:
            def __init__(self):self.used=[]
            def __call__(self,path):
                obj=m.read(path)
                if str(path)not in parents:return obj
                module,mapping=parents[str(path)];r=module.PARENT;m.verify(r,True)if module is not b else m.verify(r)
                view,proof=module.exact_manifest_view(r,obj,mapping);self.used.append(str(path));return view
            def require_both_used(self):
                m.need(set(self.used)==set(parents),"Synthetic three-context caller must actually use every parent")
            def proof(self):return dict(SYNTHETIC_SOFTWARE_ONLY=True,used_parent_paths=self.used,raw_JSON_changed=False)
        return bundle,config,SyntheticExactThreeReader(),parents,fr,five,lineage
    def five_parent(self):
        import hashlib,io,tarfile
        bundle,config,oldreader,parents,fr,five,lineage=self.three();a=bundle.a;specs=[];rows_all=[]
        for number in range(2):
            payloads=[("archive"+str(number)+"/raw.txt",b"SYNTHETIC_TAR_MEMBER_BYTES"),("archive"+str(number)+"/old.json",b'{"path":"/UNRECOVERED_PAYLOAD_NOT_PARSED","bytes":1,"sha256":"'+b"0"*64+b'"}')]
            path=self.d/("synthetic"+str(number)+".tar.gz")
            with tarfile.open(path,"w:gz")as tar:
                for name,data in payloads:
                    info=tarfile.TarInfo(name);info.size=len(data);tar.addfile(info,io.BytesIO(data))
            path.chmod(0o444);tarrec=m.rec(path)
            rows=[dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())for name,data in payloads]
            raw=dict(archive=tarrec["path"],archive_bytes=tarrec["bytes"],archive_sha256=tarrec["sha256"],member_count=len(rows),members=rows,unchanged_scalar="SYNTHETIC_NAMESPACE_ONLY")
            parent=self.file("synthetic_archive"+str(number)+".members.json",json.dumps(raw).encode(),True)
            specs.append(dict(parent_manifest=parent,archive_receipt=tarrec,member_count=len(rows)));rows_all.append(rows)
        a.ARCHIVES=specs
        producer=dict(schema=a.PROOF_SCHEMA,status=a.PROOF_STATUS,historical_archive_context_parent_n=2,archive_member_n=a.total(),all_regular_members_exactly_verified=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,archives=[dict(**spec,regular_members=[{k:v for k,v in a.entry(spec,i,r).items()if k!="source_parent"}for i,r in enumerate(rows)],directory_n=0,archive_bytes_verified_before_and_after=True,extracted=False,archived_JSON_payload_parsed=False)for spec,rows in zip(specs,rows_all)])
        producer_receipt=m.dump(self.d/"synthetic_archive_producer.json",producer)
        mapping=dict(schema=a.SCHEMA,status=a.STATUS,current_declared_graph_only=True,historical_archive_context_parent_n=2,archive_member_n=a.total(),all588_declared_member_edges_observed=True,all588_member_bytes_independently_verified_in_archives=True,original_index_JSON_bytes_unchanged=True,archive_extracted=False,archived_JSON_payload_parsed=False,current_file_restored=False,current_execution_authorized=False,new_scientific_inference=False,unknown_relative_edges_allowed=False,external_files_read=False,archive_member_verification=producer_receipt,archives=[dict(**spec,entries=[a.entry(spec,i,r)for i,r in enumerate(rows)])for spec,rows in zip(specs,rows_all)],accepted_lineage_receipts=lineage[:4],producer_executed_source=lineage[0],producer_actual_software_gate=lineage[1],source_graph_selector=lineage[2],prior_accepted_inclusion=lineage[3])
        ar=m.dump(self.d/"synthetic_archive_map.json",mapping);a.verify_mapping_receipt(ar)
        obj=m.read(config["path"]);obj["files"] += [dict(receipt=r,classification="EVIDENCE")for r in [ar,producer_receipt,*[r for spec in specs for r in (spec["parent_manifest"],spec["archive_receipt"])]]]
        config=m.dump(self.d/"five_parent_config.json",obj);archiveparents={spec["parent_manifest"]["path"]:spec["parent_manifest"]for spec in specs};allparents={**parents,**archiveparents}
        class SyntheticFiveParentReader:
            def __init__(self):self.used=[]
            def __call__(self,path):
                if str(path)in archiveparents:
                    parent=archiveparents[str(path)];m.verify(parent,True);view,proof=a.exact_manifest_view(parent,m.read(path),mapping);self.used.append(str(path));return view
                obj=oldreader(path)
                if str(path)in parents:self.used.append(str(path))
                return obj
            def require_both_used(self):m.need(set(self.used)==set(allparents),"All five synthetic parents must really be traversed")
            def proof(self):return dict(SYNTHETIC_SOFTWARE_ONLY=True,used_parent_paths=self.used,raw_JSON_changed=False)
        return bundle,config,SyntheticFiveParentReader(),allparents,fr,five,lineage,ar
    def test_44_actual_frozen_validate_all_three_views_preserves_raw_JSON(self):
        bundle,config,reader,parents,fr,five,lineage=self.three();before={p:Path(p).read_bytes()for p in parents};api=m.load("synthetic_three_context_core",m.LIB/"delivery_core_v2.py")
        self.assertEqual([Path(r["path"]).suffix for r in five],[".txt",".txt",".txt",".json",".json"])
        for i,r in enumerate(five):
            if Path(r["path"]).suffix==".json":self.assertIsInstance(json.loads(Path(r["path"]).read_text()),dict)
            else:self.assertEqual(Path(r["path"]).read_bytes(),("SYNTHETIC_EVIDENCE_"+str(i)).encode())
        inventory=json.loads(Path(five[4]["path"]).read_text());self.assertIs(inventory["SYNTHETIC_SOFTWARE_ONLY"],True);self.assertEqual(inventory["evidence_name"],"public_source_inventory_5001.json")
        with self.git_fixture(api):result,_=m.validate_archive_context(api,config["path"],str(self.d/"validation.json"),reader,dict(SYNTHETIC=True))
        self.assertEqual(result["status"],"FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY")
        self.assertEqual(before,{p:Path(p).read_bytes()for p in parents});self.assertEqual(set(reader.used),set(parents))
        obj=m.read(config["path"]);paths=[item["receipt"]["path"]for item in obj["files"]]
        self.assertEqual(len(paths),len(set(paths)));self.assertEqual(paths.count(bundle.h.PARENT["path"]),1)
        for kind in ("duplicate","identity_conflict"):
            with self.subTest(kind=kind):
                fork=copy.deepcopy(obj);extra=copy.deepcopy(next(item for item in obj["files"]if item["receipt"]==bundle.h.PARENT))
                if kind=="identity_conflict":extra["receipt"]["sha256"]="f"*64
                fork["files"].append(extra);bad=self.file("bad_shared_"+kind+".json",json.dumps(fork).encode())
                expected="Duplicate packaged path"if kind=="duplicate"else"Receipt mismatch"
                with self.git_fixture(api),self.assertRaisesRegex(ValueError,expected):m.validate_archive_context(api,bad["path"],str(self.d/("bad_validation_"+kind+".json")),reader,dict(SYNTHETIC=True))
    def test_45_unknown_current_external_still_fails_core(self):
        bundle,config,reader,parents,fr,five,lineage=self.three(True);api=m.load("synthetic_three_context_unknown",m.LIB/"delivery_core_v2.py");original=api.read
        with self.git_fixture(api),self.assertRaises(ValueError):m.validate_archive_context(api,config["path"],str(self.d/"validation.json"),reader,{})
        self.assertIs(api.read,original);self.assertFalse((self.d/"validation_context.json").exists())
    def test_46_missing_current_txt_evidence_blocks_real_core(self):
        bundle,config,reader,parents,fr,five,lineage=self.three();Path(five[0]["path"]).unlink();api=m.load("synthetic_three_missing_byte",m.LIB/"delivery_core_v2.py")
        original=api.read
        with self.git_fixture(api),self.assertRaises(FileNotFoundError):m.validate_archive_context(api,config["path"],str(self.d/"validation.json"),reader,{})
        self.assertIs(api.read,original);self.assertFalse((self.d/"validation.json").exists());self.assertFalse((self.d/"validation_context.json").exists())
    def test_47_all_five_txt_json_archive_universe_mandatory(self):
        bundle,config,reader,parents,fr,five,lineage,ar=self.five_parent();obj=m.read(config["path"]);self.assertEqual(len(wrapper.require_current_context_archive(obj,bundle)),12)
        obj["files"]=[x for x in obj["files"]if x["receipt"]!=five[0]]
        with self.assertRaises(ValueError):wrapper.require_current_context_archive(obj,bundle)
    def test_48_three_context_current_five_restore_reads_only_archived_bytes(self):
        bundle,config,reader,parents,fr,five,lineage=self.three();root=self.d/"restore";root.mkdir();index=[]
        for i,r in enumerate([fr,bundle.f.PARENT,*five,*lineage]):
            target=root/str(i);target.write_bytes(Path(r["path"]).read_bytes());target.chmod(0o444);index.append(dict(logical=r,restored_relative=str(i)))
        for r in [fr,bundle.f.PARENT,*five]:Path(r["path"]).unlink()
        _,proof=bundle.f.verify_restored_mapping(fr,root,index);self.assertTrue(proof["no_live_root_fallback"]);self.assertEqual(len(proof["contexts"]),5)
    def test_49_missing_restored_current_child_has_no_live_rescue(self):
        bundle,config,reader,parents,fr,five,lineage=self.three();root=self.d/"restore";root.mkdir();index=[]
        for i,r in enumerate([fr,bundle.f.PARENT,*five,*lineage]):
            if r==five[0]:continue
            target=root/str(i);target.write_bytes(Path(r["path"]).read_bytes());target.chmod(0o444);index.append(dict(logical=r,restored_relative=str(i)))
        self.assertTrue(Path(five[0]["path"]).exists())
        with self.assertRaises(ValueError):bundle.f.verify_restored_mapping(fr,root,index)
    def test_50_final_delivery_requires_actual_derived_pipeline_gate(self):
        inclusion=self.file("source_inclusion.json",b"{}");derived=self.file("derived.json",b"{}");pipe=self.file("pipeline.py",b"synthetic")
        accepted=dict(schema="final-source-closure-acceptance.v3",status="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED",source_inclusion=inclusion,source_issues=0,mandatory_derived_pipeline_qualification=dict(acceptance=derived,all_eight_actual_suite_rows_verified=True,derived_pipeline=pipe,source_dependencies=[{"SYNTHETIC_ONLY":True}],failed_predecessor={"status":"ACTUAL_FAILED13303_V1_PRESERVED_NOT_QUALIFIED"}))
        self.assertEqual(m.mandatory_final_source_shape(accepted,inclusion,derived)["derived_pipeline"],pipe)
        for value in ({},dict(acceptance=inclusion,all_eight_actual_suite_rows_verified=True,derived_pipeline=pipe),dict(acceptance=derived,all_eight_actual_suite_rows_verified=False,derived_pipeline=pipe)):
            with self.subTest(value=value),self.assertRaises(ValueError):m.mandatory_final_source_shape({**accepted,"mandatory_derived_pipeline_qualification":value},inclusion,derived)
    def test_51_third_parent_unknown_field_before_dedup(self):
        bundle,config,reader,parents,fr,five,lineage=self.three();mapping=m.read(fr["path"]);raw=m.read(bundle.f.PARENT["path"])["files"][0]
        with self.assertRaises(ValueError):bundle.f.normalise_edge(raw,bundle.f.PARENT,["wrong","0"],mapping)

class ArchiveCallerContracts(ThreeContextComposerContracts):
    def test_52_actual_frozen_validate_five_parents_keeps_index_and_tar_bytes(self):
        bundle,config,reader,parents,fr,five,lineage,ar=self.five_parent();before={p:Path(p).read_bytes()for p in parents}
        tarbefore={s["archive_receipt"]["path"]:Path(s["archive_receipt"]["path"]).read_bytes()for s in bundle.a.ARCHIVES}
        api=m.load("synthetic_five_parent_actual_core",m.LIB/"delivery_core_v2.py")
        with self.git_fixture(api):result,_=m.validate_archive_context(api,config["path"],str(self.d/"validation.json"),reader,{"SYNTHETIC":True})
        self.assertEqual(result["status"],"FINAL_DELIVERY_CONFIG_CONTENT_ACCEPTED_COMPUTATIONAL_ONLY");self.assertEqual(set(reader.used),set(parents))
        self.assertEqual(before,{p:Path(p).read_bytes()for p in parents});self.assertEqual(tarbefore,{p:Path(p).read_bytes()for p in tarbefore})
        paths=[item["receipt"]["path"]for item in m.read(config["path"])["files"]];self.assertEqual(len(paths),len(set(paths)));self.assertEqual(paths.count(bundle.h.PARENT["path"]),1)
    def test_53_both_tar_and_indices_required_in_archive(self):
        bundle,config,reader,parents,fr,five,lineage,ar=self.five_parent();obj=m.read(config["path"])
        self.assertEqual(len(wrapper.require_current_context_archive(obj,bundle)),12)
        for r in [r for s in bundle.a.ARCHIVES for r in (s["parent_manifest"],s["archive_receipt"])]:
            fork=copy.deepcopy(obj);fork["files"]=[x for x in fork["files"]if x["receipt"]!=r]
            with self.subTest(path=r["path"]),self.assertRaises(ValueError):wrapper.require_current_context_archive(fork,bundle)
    def test_54_restore_both_archives_streams_bytes_without_any_live_rescue(self):
        bundle,config,reader,parents,fr,five,lineage,ar=self.five_parent();mapping=m.read(ar["path"]);root=self.d/"archive_restore";root.mkdir();index=[]
        receipts=[ar,mapping["archive_member_verification"],*mapping["accepted_lineage_receipts"],*[r for s in bundle.a.ARCHIVES for r in (s["parent_manifest"],s["archive_receipt"])]]
        for i,r in enumerate(receipts):
            target=root/str(i);target.write_bytes(Path(r["path"]).read_bytes());target.chmod(0o444);index.append(dict(logical=r,restored_relative=str(i)))
        for r in receipts:Path(r["path"]).unlink()
        _,proof=bundle.a.verify_restored_mapping(ar,root,index)
        self.assertTrue(proof["no_live_root_fallback"]);self.assertTrue(proof["all_member_bytes_verified"]);self.assertEqual(proof["member_n"],4)
    def test_55_missing_restored_tar_cannot_fall_back_to_live(self):
        bundle,config,reader,parents,fr,five,lineage,ar=self.five_parent();mapping=m.read(ar["path"]);root=self.d/"archive_restore";root.mkdir();index=[];omitted=bundle.a.ARCHIVES[0]["archive_receipt"]
        receipts=[ar,mapping["archive_member_verification"],*mapping["accepted_lineage_receipts"],*[r for s in bundle.a.ARCHIVES for r in (s["parent_manifest"],s["archive_receipt"])]]
        for i,r in enumerate(receipts):
            if r==omitted:continue
            target=root/str(i);target.write_bytes(Path(r["path"]).read_bytes());target.chmod(0o444);index.append(dict(logical=r,restored_relative=str(i)))
        self.assertTrue(Path(omitted["path"]).exists())
        with self.assertRaises(ValueError):bundle.a.verify_restored_mapping(ar,root,index)
    def test_56_new_five_parent_reader_restored_in_finally_on_unknown_member(self):
        bundle,config,reader,parents,fr,five,lineage,ar=self.five_parent();obj=m.read(config["path"]);foreign=self.file("foreign.json",json.dumps({"path":"UNKNOWN_CURRENT_RELATIVE","bytes":1,"sha256":"0"*64}).encode(),True)
        obj["files"].append(dict(receipt=foreign,classification="EVIDENCE"));newconfig=m.dump(self.d/"foreign_config.json",obj);api=m.load("synthetic_unknown_member_core",m.LIB/"delivery_core_v2.py");original=api.read
        with self.git_fixture(api),self.assertRaises(ValueError):m.validate_archive_context(api,newconfig["path"],str(self.d/"validation.json"),reader,{})
        self.assertIs(api.read,original)
    def test_57_archive_current_relative_edge_is_validated_before_dedup(self):
        bundle,config,reader,parents,fr,five,lineage,ar=self.five_parent();mapping=m.read(ar["path"]);spec=bundle.a.ARCHIVES[0];raw=m.read(spec["parent_manifest"]["path"])["members"][0]
        result,proof=bundle.c.normalize_edge(raw,spec["parent_manifest"],["members","0"],{}, {},{},mapping);self.assertIsNone(result);self.assertFalse(proof["current_file_restored"])
        with self.assertRaises(ValueError):bundle.c.normalize_edge(raw,spec["parent_manifest"],["other","0"],{}, {},{},mapping)
    def test_58_mapper_source_universe_exact14_cannot_omit_archive_helper(self):
        api=m.context_api();pins=m.sources()["context_API_dependencies"]
        self.assertEqual(len(pins),14)
        with self.assertRaises(ValueError):api.executed_mapper_binding(pins[:-1],pins,m.identity)
    def test_59_final_source_old_seven_rows_or_missing_named_dependency_rejected(self):
        inclusion=self.file("incl.json",b"{}");derived=self.file("derived.json",b"{}");pipe=self.file("pipeline.py",b"synthetic")
        proof=dict(acceptance=derived,all_eight_actual_suite_rows_verified=True,derived_pipeline=pipe,source_dependencies=[{"SYNTHETIC":True}],failed_predecessor={"status":"ACTUAL_FAILED13303_V1_PRESERVED_NOT_QUALIFIED"})
        accepted=dict(schema="final-source-closure-acceptance.v3",status="FINAL_SOURCE_SET_AUDITED_NOT_STAGED_NOT_PUBLISHED",source_inclusion=inclusion,source_issues=0,mandatory_derived_pipeline_qualification=proof)
        self.assertEqual(m.mandatory_final_source_shape(accepted,inclusion,derived),proof)
        for key,value in (("source_dependencies",[]),("failed_predecessor",{}),("all_eight_actual_suite_rows_verified",False)):
            fork=copy.deepcopy(accepted);fork["mandatory_derived_pipeline_qualification"][key]=value
            with self.assertRaises(ValueError):m.mandatory_final_source_shape(fork,inclusion,derived)
for _inherited in [n for n in ThreeContextComposerContracts.__dict__ if n.startswith("test_")]:
    setattr(ArchiveCallerContracts,_inherited,None)

class ControllerAmendmentContracts(unittest.TestCase):
    def case(self):
        def r(name):return dict(path=str(m.R/"synthetic_controller_contracts"/name),bytes=1,sha256="a"*64)
        q=m.CONTROLLER_AMENDMENT_ACCEPTANCE
        a=dict(schema="root-controller-metadata-amendment-CPU-qualification.v1",status="ROOT_ACTUAL_EVALUATE_CONTROLLER_SINGLE_DESCRIPTOR_ADDITION_CPU_ACCEPTED",actual_job_id="13311",all_original_submission_fields_and_journal_entries_unchanged=True,allocation=dict(slurm_job_id="13315",allocated_GPU_count=0,allocated_CPU_count=1),amendment=r("amendment.json"),archived_original_controller=r("old.json"),amended_controller=r("new.json"),actual_design_CPU_acceptance=r("design.json"),journal=r("journal3.json"))
        old=dict(schema="reference_free_root_model_submission.v1",job_id="13311",stage="evaluate",root_owned_primary=True,design_audit_acceptance_path=a["actual_design_CPU_acceptance"]["path"],submit_argv=["sbatch","UNCHANGED",a["actual_design_CPU_acceptance"]["path"]],upstream=r("manifest.json"),design_stage_result=r("stage.json"),source_manifest=r("source.json"),preflight_acceptance=r("preflight.json"))
        new=dict(old,design_audit_acceptance=a["actual_design_CPU_acceptance"])
        amend=dict(schema="root-controller-traceable-metadata-only-amendment.v1",original_controller_exact_byte_archive=a["archived_original_controller"],amended_controller=a["amended_controller"],journal=a["journal"],addition_only={"design_audit_acceptance":a["actual_design_CPU_acceptance"]},original_other_fields_unchanged=True,journal_bytes_unchanged=True,new_GPU_job_submitted=False,scientific_settings_changed=False,actual_original_GPU_job_id="13311",original_controller_logical_path=a["amended_controller"]["path"])
        design=dict(schema="reference_free_e2e_design_cpu_gate.v1",status="REFERENCE_FREE_E2E_ACTUAL_DESIGN_CPU_CONTENT_ACCEPTED",slurm_CPU_job_id="13309",GPU_allocated=0,actual_design_manifest=old["upstream"],actual_design_stage_result=old["design_stage_result"],source_manifest=old["source_manifest"],preflight_acceptance=old["preflight_acceptance"])
        j3=dict(schema="root-current-gpu-submission-journal.v1",authority_root=str(m.R),scope_start_utc="FIXED",entries=[dict(submission_id="e2e_evaluate_13311",receipt_path=a["amended_controller"]["path"])])
        j4=dict(j3,previous_journal_path=a["journal"]["path"],metadata_only_controller_amendment_CPU_qualifications=[q])
        return [q,a,amend,old,new,design,j3,j4]
    def test_controller_exact_single_tuple_addition_and_universe(self):
        proof=m.controller_amendment_content(*self.case());self.assertFalse(proof["new_GPU_job_submitted"]);self.assertEqual(proof["only_added_field"],"design_audit_acceptance")
    def test_controller_other_field_or_argv_change_rejected(self):
        for field,value in (("job_id","999"),("submit_argv",["changed"]),("unrelated_field",True)):
            args=self.case();args[4][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):m.controller_amendment_content(*args)
    def test_controller_missing_or_fork_design_tuple_rejected(self):
        for change in (None,{"path":"/wrong","bytes":1,"sha256":"b"*64}):
            args=self.case();args[4]["design_audit_acceptance"]=change
            with self.assertRaises(ValueError):m.controller_amendment_content(*args)
    def test_controller_journal_new_submission_or_qualification_fork_rejected(self):
        for kind in ("entries","qualification","predecessor"):
            args=self.case();args[7]=dict(args[7])
            if kind=="entries":args[7]["entries"]=[]
            elif kind=="qualification":args[7]["metadata_only_controller_amendment_CPU_qualifications"]=[]
            else:args[7]["previous_journal_path"]="/wrong"
            with self.assertRaises(ValueError):m.controller_amendment_content(*args)
    def test_controller_actual_design_lineage_fork_rejected(self):
        args=self.case();args[5]["actual_design_stage_result"]={"path":"/different","bytes":1,"sha256":"e"*64}
        with self.assertRaises(ValueError):m.controller_amendment_content(*args)
    def test_controller_actual_gpu_or_scientific_change_rejected(self):
        for kind in ("GPU","science","allocation"):
            args=self.case()
            if kind=="GPU":args[2]["new_GPU_job_submitted"]=True
            elif kind=="science":args[2]["scientific_settings_changed"]=True
            else:args[1]["allocation"]["allocated_GPU_count"]=1
            with self.assertRaises(ValueError):m.controller_amendment_content(*args)
    def test_controller_restore_without_explicit_index_reader_rejected(self):
        binding=dict(qualification=m.CONTROLLER_AMENDMENT_ACCEPTANCE,journal4=dict(path=m.CONTROLLER_JOURNAL4_PATH,bytes=1,sha256="a"*64))
        with self.assertRaisesRegex(ValueError,"explicit restored-index"):m.qualify_controller_amendment(binding,restore=True)
