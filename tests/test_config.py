import json

from utils.config import load_apps_config


def test_load_apps_config_applies_env_overrides(tmp_path, monkeypatch):
    config_data = {
        "calculadora": {
            "name_of_program": "calc.exe",
            "name_of_process": "CalculatorApp.exe"
        }
    }
    config_path = tmp_path / "apps.json"
    config_path.write_text(json.dumps(config_data), encoding="utf-8")

    monkeypatch.setenv("CALCULADORA_PROGRAM", "custom_calc.exe")
    monkeypatch.setenv("CALCULADORA_PROCESS", "CustomCalculatorApp.exe")

    apps = load_apps_config(path=str(config_path))

    assert apps["calculadora"]["name_of_program"] == "custom_calc.exe"
    assert apps["calculadora"]["name_of_process"] == "CustomCalculatorApp.exe"
