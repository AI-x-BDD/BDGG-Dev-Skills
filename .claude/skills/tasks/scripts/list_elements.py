# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""列出一個 spec package 裡規格檔的每一個介面元素,錨點的寫法和 tasks.md 的 ⚙ 一致。

讀 contracts/ 底下的 *.asyncapi.yaml、*.openapi.yaml、*.dbml,prototype*/ 底下的 *.html 與 *.css,
deploy/ 底下(含子資料夾)的 compose.yaml、*.conf 與 Dockerfile。

輸出分成兩類:
  required  每一個都要在 tasks.md 的介面覆蓋表上出現:AsyncAPI 的 operations、OpenAPI 的 path + method、
            DBML 的 Table、原型的每一個 data-state、compose 的 services、反向代理的 location
  anchors   可以拿來當 ⚙ 的錨點、不強制覆蓋:schema、channel、servers、DBML 欄位、原型的 #id 與 .class、
            CSS 的 :root 與 @media、compose 服務底下的欄位、Dockerfile 指令
結果以 JSON 寫到 stdout;spec package 裡找不到任何規格檔時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
DBML_TABLE = re.compile(r"^\s*Table\s+(\"[^\"]+\"|[\w.]+)", re.MULTILINE)
DBML_COLUMN = re.compile(r"^\s*(\"[^\"]+\"|\w+)\s+[\w(),.\[\]]+")
DATA_STATE = re.compile(r'data-state="([^"]+)"')
HTML_ID = re.compile(r'\bid="([^"]+)"')
HTML_CLASS = re.compile(r'\bclass="([^"]+)"')
CSS_AT_MEDIA = re.compile(r"(@media[^{]+?)\s*\{")
NGINX_LOCATION = re.compile(r"^\s*location\s+([^{]+?)\s*\{", re.MULTILINE)
DOCKER_INSTRUCTION = re.compile(r"^\s*([A-Z]+)\s", re.MULTILINE)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: {path} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def read_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(read_text(path))
    except yaml.YAMLError as error:
        print(f"錯誤: {path} 不是合法的 YAML:{error}。請先修好這個檔再執行。", file=sys.stderr)
        sys.exit(2)
    return data if isinstance(data, dict) else {}


def collect(package: Path) -> tuple[list[dict], list[dict]]:
    required: list[dict] = []
    anchors: list[dict] = []

    def add(bucket: list[dict], path: Path, anchor: str, kind: str) -> None:
        item = {"file": path.relative_to(package).as_posix(), "anchor": anchor, "kind": kind}
        if item not in bucket:
            bucket.append(item)

    contracts = package / "contracts"
    for path in sorted(contracts.glob("*.asyncapi.yaml")) + sorted(contracts.glob("*.asyncapi.yml")):
        data = read_yaml(path)
        for name in data.get("operations") or {}:
            add(required, path, f"operations.{name}", "asyncapi-operation")
        for name in (data.get("components") or {}).get("schemas") or {}:
            add(anchors, path, f"components.schemas.{name}", "schema")
        for name, channel in (data.get("channels") or {}).items():
            add(anchors, path, f"channels.{name}", "channel")
            if isinstance(channel, dict) and "address" in channel:
                add(anchors, path, f"channels.{name}.address", "channel")
        if "servers" in data:
            add(anchors, path, "servers", "servers")
        if isinstance(data.get("info"), dict) and "description" in data["info"]:
            add(anchors, path, "info.description", "info")

    for path in sorted(contracts.glob("*.openapi.yaml")) + sorted(contracts.glob("*.openapi.yml")):
        data = read_yaml(path)
        for route, item in (data.get("paths") or {}).items():
            for method in item or {}:
                if method.lower() in HTTP_METHODS:
                    add(required, path, f"paths.{route}.{method.lower()}", "openapi-operation")
        for name in (data.get("components") or {}).get("schemas") or {}:
            add(anchors, path, f"components.schemas.{name}", "schema")
        if "servers" in data:
            add(anchors, path, "servers", "servers")

    for path in sorted(contracts.glob("*.dbml")):
        text = read_text(path)
        for match in DBML_TABLE.finditer(text):
            table = match.group(1).strip('"')
            add(required, path, f"Table {table}", "dbml-table")
            body = text[match.end():].split("{", 1)[-1].split("}", 1)[0]
            for line in body.splitlines():
                column = DBML_COLUMN.match(line)
                if column and not line.strip().lower().startswith(("indexes", "note", "ref")):
                    add(anchors, path, f"Table {table}.{column.group(1).strip(chr(34))}", "dbml-column")

    for folder in sorted(p for p in package.glob("prototype*") if p.is_dir()):
        for path in sorted(folder.glob("*.html")):
            text = read_text(path)
            for state in DATA_STATE.findall(text):
                add(required, path, f'[data-state="{state}"]', "prototype-state")
            for element_id in HTML_ID.findall(text):
                add(anchors, path, f"#{element_id}", "prototype-id")
            for classes in HTML_CLASS.findall(text):
                for name in classes.split():
                    add(anchors, path, f".{name}", "prototype-class")
        for path in sorted(folder.glob("*.css")):
            text = read_text(path)
            if re.search(r":root\s*\{", text):
                add(anchors, path, ":root", "css")
            for media in CSS_AT_MEDIA.findall(text):
                add(anchors, path, " ".join(media.split()), "css")

    deploy = package / "deploy"
    compose_names = {"compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"}
    for path in sorted(p for p in deploy.rglob("*") if p.name in compose_names and p.is_file()):
        for service, body in (read_yaml(path).get("services") or {}).items():
            add(required, path, f"services.{service}", "compose-service")
            for key in body or {}:
                add(anchors, path, f"services.{service}.{key}", "compose-field")
    for path in sorted(deploy.rglob("*.conf")):
        for location in NGINX_LOCATION.findall(read_text(path)):
            add(required, path, f"location {' '.join(location.split())}", "proxy-location")
    for path in sorted(deploy.rglob("Dockerfile*")):
        for instruction in DOCKER_INSTRUCTION.findall(read_text(path)):
            add(anchors, path, instruction, "dockerfile")
    return required, anchors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--package", required=True, type=Path, help="spec package 的路徑(spec.md 所在的資料夾)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not (args.package / "spec.md").is_file():
        print(f"錯誤: {args.package} 底下沒有 spec.md。--package 要給 spec.md 所在的資料夾。", file=sys.stderr)
        return 2

    required, anchors = collect(args.package)
    if not required and not anchors:
        print(
            f"錯誤: {args.package} 底下找不到任何規格檔。請確認 contracts/、prototype*/、deploy/ 是否在這個資料夾裡。",
            file=sys.stderr,
        )
        return 1

    counts: dict[str, int] = {}
    for item in required:
        counts[item["kind"]] = counts.get(item["kind"], 0) + 1
    print(f"必須覆蓋的介面元素 {len(required)} 個,可當錨點的 {len(anchors)} 個", file=sys.stderr)
    json.dump(
        {"package": str(args.package), "required_counts": counts, "required": required, "anchors": anchors},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
