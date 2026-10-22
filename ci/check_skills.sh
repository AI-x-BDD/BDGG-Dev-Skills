#!/bin/sh
# 逐支檢查 .agents/skills 與 .claude/skills 底下的 skill:SOP、Rule File、樣板與腳本照 skill-form 系列的檢查器,
# 兩份同名 skill 的內容要完全相同。任何一項不過就 exit 1,合併機器人看到 pipeline 失敗就不合。
set -u
forms=.agents/skills
fail=0

check() {
    label=$1
    shift
    if ! out=$("$@" 2>&1); then
        echo "不過 $label"
        echo "$out" | head -40
        fail=1
    fi
}

for dir in .agents/skills/*/ .claude/skills/*/; do
    dir=${dir%/}
    [ -f "$dir/SKILL.md" ] || continue
    check "$dir SOP" python3 "$forms/skill-form-sop/scripts/render_sop_diagram.py" --file "$dir/SKILL.md" --check
    [ -d "$dir/templates" ] && check "$dir 樣板" python3 "$forms/skill-form-template/scripts/check_templates.py" --skill "$dir"
    [ -d "$dir/scripts" ] && check "$dir 腳本" python3 "$forms/skill-form-script/scripts/check_scripts.py" --skill "$dir"
    for rule in "$dir"/rules/*.md; do
        [ -f "$rule" ] && check "$rule" python3 "$forms/skill-form-rule/scripts/check_rule_file.py" --file "$rule"
    done
done

for dir in .agents/skills/*/; do
    name=$(basename "$dir")
    if [ ! -d ".claude/skills/$name" ]; then
        echo "不過 .claude/skills/$name 不存在(兩份要同步)"
        fail=1
    elif ! diff -r -x __pycache__ ".agents/skills/$name" ".claude/skills/$name" >/dev/null; then
        echo "不過 .agents/skills/$name 與 .claude/skills/$name 內容不同(兩份要同步)"
        diff -rq -x __pycache__ ".agents/skills/$name" ".claude/skills/$name" | head -20
        fail=1
    fi
done
for dir in .claude/skills/*/; do
    name=$(basename "$dir")
    [ -d ".agents/skills/$name" ] || { echo "不過 .agents/skills/$name 不存在(兩份要同步)"; fail=1; }
done

[ "$fail" -eq 0 ] && echo "全部通過"
exit "$fail"
