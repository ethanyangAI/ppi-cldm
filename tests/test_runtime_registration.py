import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock
import pytest
from ppiblocker.common import EvidenceError

PATH=Path(__file__).resolve().parents[1]/"scripts/register_runtime_locks.py"
spec=importlib.util.spec_from_file_location("runtime_registration_under_test",PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def lock(root,component,value):
    path=root/"source/environment"/f"runtime-lock-{component}.json"
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
    return path

def test_register_missing_component_preserves_existing_reviewed_locks(tmp_path,monkeypatch):
    core=lock(tmp_path,"core",{"stable":"core"});rfd=lock(tmp_path,"rfd",{"stable":"rfd"})
    before=(core.read_bytes(),rfd.read_bytes())
    collect=Mock(return_value={"component":"boltz","verified":True})
    molecule=Mock()
    monkeypatch.setattr(module,"collect_runtime",collect)
    monkeypatch.setattr(module,"verify_boltz_archive",molecule)
    assert module.main(["--root",str(tmp_path),"--initialize-reviewed","--component","boltz","--component","boltz"])==0
    assert (core.read_bytes(),rfd.read_bytes())==before
    assert json.loads((tmp_path/"source/environment/runtime-lock-boltz.json").read_text())==collect.return_value
    collect.assert_called_once_with(tmp_path.resolve(),"boltz")
    molecule.assert_called_once_with(tmp_path.resolve())

def test_existing_selected_lock_rejected_before_probing(tmp_path,monkeypatch):
    p=lock(tmp_path,"rfd",{"unchanged":True});before=p.read_bytes()
    collect=Mock();molecule=Mock()
    monkeypatch.setattr(module,"collect_runtime",collect)
    monkeypatch.setattr(module,"verify_boltz_archive",molecule)
    with pytest.raises(EvidenceError,match="Refusing to overwrite"):
        module.main(["--root",str(tmp_path),"--initialize-reviewed","--component","rfd"])
    assert p.read_bytes()==before
    collect.assert_not_called();molecule.assert_not_called()

def test_atomic_writer_rejects_racing_existing_file(tmp_path):
    p=tmp_path/"runtime-lock-core.json";p.write_text("original")
    with pytest.raises(EvidenceError):module.write_new_lock(p,{"new":"disallowed"})
    assert p.read_text()=="original"
    assert not list(tmp_path.glob("*.tmp"))

def test_default_registers_all_components(tmp_path,monkeypatch):
    collect=Mock(side_effect=lambda root,c:{"component":c});molecule=Mock()
    monkeypatch.setattr(module,"collect_runtime",collect)
    monkeypatch.setattr(module,"verify_boltz_archive",molecule)
    assert module.main(["--root",str(tmp_path),"--initialize-reviewed"])==0
    assert [x.args[1] for x in collect.call_args_list]==["core","rfd","boltz"]
    molecule.assert_called_once()
    assert len(list((tmp_path/"source/environment").glob("runtime-lock-*.json")))==3
