"""Directory roots use native ChatEnv without writing a real profile."""
from pathlib import Path
import hashlib

import click
from click.testing import CliRunner
import pytest
from chatenv import EnvStore, get_paths

from chathfd import config
from chathfd.cli import main
from chathfd import download

KEY = "CHATHFD_DOWNLOAD_ROOT"
REPO = "Example/item"
META = {"sha":"a"*40,"gated":False,"siblings":[{"rfilename":"config.json","size":4}]}


def profile(root):
    return EnvStore(get_paths().envs_dir).save_active(config.ChathfdConfig,{KEY:str(root)})


def test_registered_root_field_has_dynamic_current_directory_default():
    field=config.ChathfdConfig.get_fields()[KEY]
    assert field.default=="."
    assert not field.is_sensitive


def test_unset_root_resolves_cwd_at_each_call(monkeypatch,tmp_path):
    a=tmp_path/"a";a.mkdir()
    b=tmp_path/"b";b.mkdir()
    monkeypatch.chdir(a)
    assert config.resolve_download_root()==a
    monkeypatch.chdir(b)
    assert config.resolve_download_root()==b
    assert not get_paths().home_dir.exists()


def test_active_profile_is_used_without_rewriting_it(tmp_path):
    root=tmp_path/"shared"
    path=profile(root)
    before=hashlib.sha256(path.read_bytes()).digest()
    assert config.resolve_download_root()==root
    assert hashlib.sha256(path.read_bytes()).digest()==before
    assert not root.exists()


def test_process_root_overrides_profile(monkeypatch,tmp_path):
    profile(tmp_path/"profile-root")
    monkeypatch.setenv(KEY,str(tmp_path/"process-root"))
    assert config.resolve_download_root()==tmp_path/"process-root"


def test_empty_process_root_means_current_directory(monkeypatch,tmp_path):
    profile(tmp_path/"profile-root")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(KEY,"")
    assert config.resolve_download_root()==tmp_path


def test_relative_and_home_root_are_resolved_at_call(monkeypatch,tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(KEY,"relative")
    assert config.resolve_download_root()==tmp_path/"relative"
    monkeypatch.setenv("HOME",str(tmp_path/"user-home"))
    monkeypatch.setenv(KEY,"~/cache")
    assert config.resolve_download_root()==tmp_path/"user-home/cache"


def test_explicit_final_dir_bypasses_invalid_lower_priority_root(monkeypatch,tmp_path):
    bad=tmp_path/"file";bad.write_text("existing")
    monkeypatch.setenv(KEY,str(bad))
    final=tmp_path/"exact-final"
    assert download.resolve_download_directory(REPO,final)==final
    assert not final.exists()


@pytest.mark.parametrize("kind",["file","parent-file","control"])
def test_invalid_root_fails_before_metadata(monkeypatch,tmp_path,kind):
    bad=tmp_path/"file";bad.write_text("existing")
    value=str(bad) if kind=="file" else (str(bad/"child") if kind=="parent-file" else str(tmp_path/"bad\npath"))
    monkeypatch.setenv(KEY,value)
    calls=[]
    monkeypatch.setattr(download,"fetch_metadata",lambda *args:calls.append(args) or META)
    result=CliRunner().invoke(main,["download",REPO,"--dry-run","-I"])
    assert result.exit_code!=0
    assert "directory" in result.output.lower() or KEY in result.output
    assert calls==[]


@pytest.mark.parametrize("repo_type",["model","dataset"])
def test_default_repo_layout_has_no_type_subdirectory(monkeypatch,tmp_path,repo_type):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(download,"fetch_metadata",lambda *args:META)
    result=CliRunner().invoke(main,["download",REPO,"--repo-type",repo_type,"--dry-run","-I"])
    assert result.exit_code==0,result.output
    assert str(tmp_path/"Example/item") in result.output
    assert not (tmp_path/"Example").exists()
    assert not (tmp_path/"models").exists()
    assert not (tmp_path/"datasets").exists()


def test_cli_and_python_api_share_profile_destination(monkeypatch,tmp_path,capsys):
    root=tmp_path/"shared"
    profile(root)
    monkeypatch.setattr(download,"fetch_metadata",lambda *args:META)
    result=CliRunner().invoke(main,["download",REPO,"--dry-run","-I"])
    assert result.exit_code==0,result.output
    assert str(root/"Example/item") in result.output
    download.download_repo(REPO,"model","main",download.DEFAULT_ENDPOINT,None,(),(),4,5,True,False)
    assert str(root/"Example/item") in capsys.readouterr().out
    assert not root.exists()


def test_forced_directory_prompt_shows_effective_config_default(monkeypatch,tmp_path):
    import chatstyle.core.interactive as core
    from chatstyle.input import resolve as resolver
    root=tmp_path/"shared";profile(root)
    monkeypatch.setattr(core,"is_interactive_available",lambda:True)
    paths=[]
    def ask_path(message,default=""):
        paths.append(default)
        return default
    monkeypatch.setattr(resolver.prompt_runtime,"ask_path",ask_path)
    monkeypatch.setattr(resolver.prompt_runtime,"ask_text",lambda message,default="",**kwargs:default)
    monkeypatch.setattr(resolver.prompt_runtime,"ask_confirm",lambda *args,**kwargs:False)
    monkeypatch.setattr(download,"fetch_metadata",lambda *args:META)
    result=CliRunner().invoke(main,["download",REPO,"-i","--repo-type","model","--dry-run"])
    assert result.exit_code==0,result.output
    assert paths==[str(root/"Example/item")]
    assert not root.exists()


def test_explicit_cli_directory_bypasses_invalid_root(monkeypatch,tmp_path):
    bad=tmp_path/"file";bad.write_text("existing")
    monkeypatch.setenv(KEY,str(bad))
    final=tmp_path/"exact-final"
    monkeypatch.setattr(download,"fetch_metadata",lambda *args:META)
    result=CliRunner().invoke(main,["download",REPO,"--local-dir",str(final),"--dry-run","-I"])
    assert result.exit_code==0,result.output
    assert str(final) in result.output
    assert str(final/"Example/item") not in result.output
    assert not final.exists()


def test_process_root_does_not_read_lower_priority_profile(monkeypatch,tmp_path):
    monkeypatch.setenv(KEY,str(tmp_path/"root"))
    monkeypatch.setattr(EnvStore,"load_active",lambda *args:pytest.fail("lower-priority profile should not be read"))
    assert config.resolve_download_root()==tmp_path/"root"


@pytest.mark.parametrize("repo",["../escape","/absolute","org/../escape"])
def test_public_directory_helper_rejects_repository_traversal(tmp_path,repo):
    with pytest.raises(click.ClickException,match="repository ID"):
        download.resolve_download_directory(repo,tmp_path/"final")
    assert not (tmp_path/"final").exists()


def test_repository_symlink_cannot_escape_configured_root(monkeypatch,tmp_path):
    root=tmp_path/"shared";(root/"Example").mkdir(parents=True)
    outside=tmp_path/"outside";outside.mkdir()
    (root/"Example/item").symlink_to(outside,target_is_directory=True)
    monkeypatch.setenv(KEY,str(root))
    with pytest.raises(click.ClickException,match="escapes"):
        download.resolve_download_directory(REPO)


def test_root_alias_itself_is_supported(monkeypatch,tmp_path):
    real=tmp_path/"real-shared";real.mkdir()
    alias=tmp_path/"shared-alias";alias.symlink_to(real,target_is_directory=True)
    monkeypatch.setenv(KEY,str(alias))
    assert download.resolve_download_directory(REPO)==real/"Example/item"


def test_resolved_control_character_root_is_rejected(monkeypatch,tmp_path):
    bad=tmp_path/"bad\npath";bad.mkdir()
    alias=tmp_path/"alias";alias.symlink_to(bad,target_is_directory=True)
    monkeypatch.setenv(KEY,str(alias))
    with pytest.raises(click.ClickException,match=KEY):
        config.resolve_download_root()


def test_config_hook_validates_real_root_without_writes(monkeypatch,tmp_path,capsys):
    root=tmp_path/"new-root"
    monkeypatch.setenv(KEY,str(root))
    EnvStore(get_paths().envs_dir).load_config(config.ChathfdConfig)
    config.ChathfdConfig.test()
    assert str(root) in capsys.readouterr().out
    assert not root.exists()


def test_config_hook_tests_selected_profile_not_active_or_process(monkeypatch,tmp_path,capsys):
    store=EnvStore(get_paths().envs_dir)
    active=tmp_path/"active";selected=tmp_path/"selected"
    profile(active)
    store.save_profile(config.ChathfdConfig,"selected",{KEY:str(selected)})
    monkeypatch.setenv(KEY,str(tmp_path/"process"))
    store.load_config(config.ChathfdConfig,profile="selected")
    config.ChathfdConfig.test()
    output=capsys.readouterr().out
    assert str(selected) in output
    assert str(active) not in output
    assert str(tmp_path/"process") not in output
    assert config.resolve_download_root()==tmp_path/"process"
    assert not selected.exists()
