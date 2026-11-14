# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""跑 spec package 的四支前置檢查:轉交同層 specify、system-analysis、testplan、tasks 四支 skill 的檢查腳本,彙整結果。

  spec.md      specify/scripts/check_spec.py
  plan.md      system-analysis/scripts/check_plan.py
  testplan.md  testplan/scripts/check_testplan.py(帶 --contracts <package>/contracts,資料夾存在時)
  tasks.md     tasks/scripts/check_tasks.py(帶 --testplan <package>/testplan.md)

結構規則只維護在產出那份檔的 skill;這支腳本只負責找到四支腳本、以 uv run 執行並彙整。
testplan.md 不存在時,testplan.md 這一筆直接判不過(tasks 與 implement 都要它),tasks.md 照舊模式檢查。
結果以 JSON 寫到 stdout:每支一筆,含是否通過與不過的項目;有任何一支不過時 exit code 是 1,
找不到同層腳本、找不到 uv 或某支腳本無法執行時是 2。
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent.parent


def checks_for(package: Path, previous_plan: Path | None) -> list[tuple[str, Path, list[str]]]:
    """回傳 (檢查的檔名, 腳本路徑, 參數) 四筆;testplan.md 不存在時,testplan.md 那一筆的參數是 None。"""
    spec = package / "spec.md"
    testplan = package / "testplan.md"
    contracts = package / "contracts"
    plan_args = ["--plan", str(package / "plan.md"), "--spec", str(spec)]
    if previous_plan:
        plan_args += ["--previous-plan", str(previous_plan)]
    testplan_args = ["--spec", str(spec), "--plan", str(testplan)] + (["--contracts", str(contracts)] if contracts.is_dir() else [])
    tasks_args = ["--tasks", str(package / "tasks.md"), "--package", str(package)] + (["--testplan", str(testplan)] if testplan.is_file() else [])
    return [
        ("spec.md", SKILLS / "specify" / "scripts" / "check_spec.py", ["--spec", str(spec)]),
        ("plan.md", SKILLS / "system-analysis" / "scripts" / "check_plan.py", plan_args),
        ("testplan.md", SKILLS / "testplan" / "scripts" / "check_testplan.py", testplan_args if testplan.is_file() else None),
        ("tasks.md", SKILLS / "tasks" / "scripts" / "check_tasks.py", tasks_args),
    ]


def failed_items(report: dict) -> list[dict]:
    """從某支檢查腳本的 JSON 取出不過的規則與它的不符項。"""
    return [
        {"rule": check.get("rule"), "violations": check.get("violations", [])}
        for check in report.get("checks", [])
        if check.get("result") == "不過"
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--package",
        required=True,
        type=Path,
        help="要分析的 spec package 資料夾,也就是 spec.md、plan.md、testplan.md、tasks.md 所在的那一層,例如 specs/001-bulls-cows-online",
    )
    parser.add_argument(
        "--previous-plan",
        type=Path,
        help="spec.md 註明建立在前一次迭代之上時,那一次迭代的 plan.md 路徑;轉交給 check_plan.py 檢查端點沿用的編號",
    )
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.package.is_dir():
        print(f"找不到 spec package 資料夾:{args.package};請給 spec.md、plan.md、testplan.md、tasks.md 所在的那一層目錄。", file=sys.stderr)
        return 2

    uv = shutil.which("uv")
    if uv is None:
        print("找不到 uv;前置檢查的腳本以 uv run 執行,請先安裝 uv(https://docs.astral.sh/uv/)後重跑。", file=sys.stderr)
        return 2

    results = []
    for target, script, script_args in checks_for(args.package, args.previous_plan):
        if script_args is None:
            results.append(
                {
                    "target": target,
                    "script": script.relative_to(SKILLS).as_posix(),
                    "passed": False,
                    "failed": [{"rule": "檔案存在", "violations": [{"item": target, "reason": f"{args.package / target} 不存在;先跑 /testplan 交出測試計劃,再跑 /tasks"}]}],
                }
            )
            continue
        if not script.is_file():
            print(
                f"找不到 {target} 的檢查腳本:{script}。"
                "analyze 要和 specify、system-analysis、testplan、tasks 放在同一個 skills 資料夾底下;請先安裝那支 skill,或把它們放到同一層後重跑。",
                file=sys.stderr,
            )
            return 2
        print(f"檢查 {target}:{script.relative_to(SKILLS).as_posix()}", file=sys.stderr)
        run = subprocess.run([uv, "run", "--quiet", str(script), *script_args], capture_output=True, text=True, encoding="utf-8")
        try:
            # 有的檢查腳本在 JSON 前面先印一行摘要,從第一個 { 開始解析
            report = json.loads(run.stdout[run.stdout.index("{"):])
        except (json.JSONDecodeError, ValueError):
            print(
                f"{target} 的檢查腳本沒有交回 JSON(exit code {run.returncode});它的錯誤訊息如下,照訊息修正輸入後重跑:\n{run.stderr.strip()}",
                file=sys.stderr,
            )
            return 2
        results.append(
            {
                "target": target,
                "script": script.relative_to(SKILLS).as_posix(),
                "passed": run.returncode == 0,
                "failed": failed_items(report),
            }
        )

    passed = all(result["passed"] for result in results)
    json.dump({"package": args.package.as_posix(), "passed": passed, "checks": results}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    failed = [result["target"] for result in results if not result["passed"]]
    print("四支前置檢查都通過" if passed else f"不過:{'、'.join(failed)}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
