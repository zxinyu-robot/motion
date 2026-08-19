#!/usr/bin/env python3
"""Restore corrupted markdown files and move metadata to document footer."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRANSCRIPTS = Path("/home/ubuntu/.cursor/projects/home-ubuntu-Downloads-motion/agent-transcripts")
FOOTER_HEADER = "## 文档元数据"
LIST_KEYS = {
    "related", "sources", "applies_to", "patent_refs", "paper_refs",
    "knowledge_refs", "benchmark_refs", "inventors",
}


def parse_yaml_block(text: str) -> dict[str, str | list[str]]:
    meta: dict[str, str | list[str]] = {}
    current_list_key: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("## ") and ":" in stripped:
            key, val = stripped[3:].split(":", 1)
            meta[key.strip()] = val.strip()
            current_list_key = None
            continue
        list_match = re.match(r"^\s*-\s+(.*)$", line)
        if list_match and current_list_key:
            lst = meta.setdefault(current_list_key, [])
            assert isinstance(lst, list)
            lst.append(list_match.group(1).strip())
            continue
        if ":" in line and not line.startswith(" "):
            key, val = line.split(":", 1)
            key, val = key.strip(), val.strip()
            if val == "":
                meta[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                meta[key] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
                current_list_key = None
            else:
                meta[key] = val
                current_list_key = None
    return meta


def extract_front_matter(content: str) -> tuple[dict[str, str | list[str]], str] | None:
    if content.startswith("---\n"):
        m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if m:
            return parse_yaml_block(m.group(1)), content[m.end() :].lstrip("\n")
        rest = content[4:].lstrip("\n")
        if rest.startswith("## id:"):
            meta, body = parse_yaml_block(rest), ""
            # broken 竞品 format: metadata until blank line before #
            lines = rest.splitlines()
            body_lines: list[str] = []
            in_meta = True
            meta_lines: list[str] = []
            for line in lines:
                if in_meta:
                    if line.startswith("# ") and not line.startswith("## id:"):
                        in_meta = False
                        body_lines.append(line)
                    elif line.strip() == "" and meta_lines:
                        continue
                    elif not line.startswith("# "):
                        meta_lines.append(line)
                    elif line.startswith("## id:"):
                        meta_lines.append(line[3:])
                else:
                    body_lines.append(line)
            meta = parse_yaml_block("\n".join(meta_lines))
            return meta, "\n".join(body_lines).lstrip("\n")
    return None


def format_footer(meta: dict[str, str | list[str]]) -> str:
    lines = ["", "---", "", FOOTER_HEADER, "", "| 字段 | 值 |", "|------|-----|"]
    list_sections: list[tuple[str, list[str]]] = []
    for key, value in meta.items():
        if isinstance(value, list):
            if value and any(str(v).startswith("http") for v in value):
                list_sections.append((key, value))
                lines.append(f"| {key} | {len(value)} 条（见下方列表） |")
            else:
                joined = "、".join(f"`{x}`" if ("/" in x or x.endswith(".md")) else x for x in value) if value else "—"
                lines.append(f"| {key} | {joined} |")
        else:
            lines.append(f"| {key} | {value} |")
    for key, items in list_sections:
        lines.extend(["", f"**{key}**", ""])
        lines.extend(f"- {item}" for item in items)
    lines.append("")
    return "\n".join(lines)


def strip_footer(content: str) -> str:
    idx = content.rfind("\n---\n\n" + FOOTER_HEADER)
    if idx != -1:
        return content[:idx].rstrip() + "\n"
    return content.rstrip() + "\n"


def apply_footer(content: str, meta: dict[str, str | list[str]] | None = None) -> str:
    parsed = extract_front_matter(content)
    if parsed:
        meta, body = parsed
    else:
        body = strip_footer(content)
        if meta is None:
            return body
    body = strip_footer(body)
    return body.rstrip() + format_footer(meta)


def transcript_write(path_suffix: str) -> str:
    best = ""
    for jsonl in TRANSCRIPTS.rglob("*.jsonl"):
        for line in jsonl.read_text(errors="ignore").splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            for part in obj.get("message", {}).get("content", []):
                if part.get("name") != "Write":
                    continue
                inp = part.get("input") or {}
                if inp.get("path", "").endswith(path_suffix) or path_suffix in inp.get("path", ""):
                    best = max(best, inp.get("contents", ""), key=len)
    return best


P0_BODY = """# P0 Benchmark 模板（Go2 单机 SLAM-Token）

> 首组数据填好后，`evidence_level` 升为 `measured`，并回链 `motion_ws` commit。

## 环境

| 项 | 值 |
|----|-----|
| 平台 | Unitree Go2 EDU |
| 边端 | Orin 【待补充型号/内存】 |
| 网关 | x86 PC 【待补充】 |
| 网络 | WiFi 【待补充带宽/RTT】 |
| SLAM 前端 | Super-LIO【当前基线；待以 stack commit 确认】 |
| Local Map 内部实现 | iVox / OctVox / Hash Map【待按实际源码确认】 |
| Planner | Nav2 2D【当前基线；待补配置与实测】 |
| Avoid | Unitree API / 固件安全能力【待补接口与触发证据】 |
| Arrival | 位置、可选朝向、规划器状态、可选语义确认【待补阈值】 |
| 空间契约 | KeyFrame + SpatialChunk/VoxelDiff【待补充版本】 |
| VLN 基线 | NaVILA / MobileVLA-R1【待补充实测选用】 |
| stack commit | 【待补充】 |
| 日期 | 【待补充】 |

## 指标

| 指标 | 目标/参考 | 实测 | 备注 |
|------|-----------|------|------|
| 定位 ATE (m) | 【待补充】 | | evo |
| 定位 RPE (m) | 【待补充】 | | evo |
| 关键帧大小 (KB) | ~200KB 级 | | 双触发后 |
| 关键帧发送频率 (Hz) | | | |
| VoxelDiff/SpatialChunk 带宽 (KB/s) | | | 记录 payload 与协议开销 |
| 每成功任务传输量 (MB/success) | | | 总传输量 / 成功任务数 |
| 边端 SLAM 延迟 (ms) | ~9.4ms 参考 | | Super-LIO |
| 端到端 waypoint 延迟 (s) | ~10s 级 VLA | | |
| 任务成功率 SR (%) | | | 明确定义成功条件 |
| 路径长度加权成功率 SPL | | | 与对应 VLN 场景一致 |
| Arrival 成功率 (%) | | | 位置/朝向/规划稳定/可选语义确认 |
| 任务完成时间 (s) | | | 成功任务统计 |
| 危险/无效 waypoint 比例 (%) | | | 不可达或触发安全拒绝 |
| 碰撞次数 | 0 | | 与固件避障触发分开统计 |
| 弱网丢包率下成功率 (%) | | | 模拟丢包 |
| 断网恢复时间 (s) | | | |
| 边端 CPU (%) | | | |
| 边端 GPU 显存 (MB) | | | |
| 固件避障触发次数 | | | L1 兜底 |
| Graph 查询命中率 (%) | | | P0 可选；命中节点含所需空间块 |
| 三维重建完整度/误差 | | | P0 可选；注明 Occupancy/TSDF/Mesh 与工具 |

## 测试场景

- [ ] 室内办公同层
- [ ] WiFi 弱网（限速/丢包）
- [ ] 断网 30s 恢复

## 闭环与失败状态

- [ ] Mapping：输出 Pose + KeyFrame + SpatialChunk/VoxelDiff
- [ ] Planner：coarse waypoint 可转换为本地轨迹
- [ ] Avoid：弱网/断网时 L1/L2 独立工作
- [ ] Arrival：按位置、可选朝向、规划器状态和语义确认判定

| 状态 | 次数 | 证据/日志 |
|---|---:|---|
| `SUCCESS` | | |
| `UNREACHABLE` | | |
| `LOST` | | |
| `NOT_FOUND` | | |
| `TIMEOUT` | | |

## 附件与回链

| 项 | 路径 |
|----|------|
| bag | 【待补充】 |
| 报告 | 【待补充】 |
| 复现命令 | 【待补充】 |
"""

P0_META = {
    "id": "BENCH-P0-001",
    "type": "benchmark",
    "stage": "validation",
    "status": "todo",
    "canonical": "true",
    "evidence_level": "idea",
    "stack": "motion_ws",
    "commit": "【待补充】",
    "updated": "2026-07-15",
    "next": "回链 Go2 部署测试的 commit、bag/日志，填写单机基线首组实测",
}

MAIN_PLAN_META = {
    "id": "PLAN-MAIN-001",
    "type": "plan",
    "stage": "design",
    "status": "in-progress",
    "canonical": "true",
    "evidence_level": "proposal",
    "confidentiality": "internal",
    "updated": "2026-07-15",
    "next": "补齐 Go2 单机基线证据，并完成 Swarm-SLAM 仿真准入评审",
}

GO2_META = {
    "id": "ARCH-SLAM-TOKEN-001",
    "type": "architecture",
    "stage": "design",
    "status": "in-progress",
    "canonical": "true",
    "evidence_level": "proposal",
    "confidentiality": "patent-sensitive",
    "updated": "2026-07-15",
}


def restore_sources() -> dict[str, tuple[str, dict | None]]:
    return {
        "01-工作计划/多机器人协同_详细技术与科研规划.md": (
            Path("/home/ubuntu/Desktop/Go2/多机器人协同_详细技术与科研规划.md").read_text(encoding="utf-8"),
            MAIN_PLAN_META,
        ),
        "02-架构设计/Go2-VLA-SLAM-Token技术方案.md": (
            transcript_write("Go2-VLA-SLAM-Token技术方案.md"),
            GO2_META,
        ),
        "40-验证/P0-Benchmark-模板.md": (P0_BODY, P0_META),
        "职业路线规划/学术生态位与三年行动计划.md": (
            transcript_write("学术生态位与三年行动计划.md"),
            None,
        ),
        "01-工作计划/3DSLAM_具身空间记忆_梳理与瞄点计划.md": (
            transcript_write("3DSLAM_具身空间记忆_梳理与瞄点计划.md"),
            None,
        ),
        "03-技术分析/外部技术与标准对标_SuperMap与ITU-T_Y3663.md": (
            transcript_write("外部技术与标准对标_SuperMap与ITU-T_Y3663.md"),
            None,
        ),
        "05-知识沉淀/deployment/CAP-DEPLOY-BRCB-001.md": (
            transcript_write("CAP-DEPLOY-BRCB-001.md"),
            None,
        ),
        "05-知识沉淀/slam/CAP-SLAM-KEYFRAME-DUAL-TRIGGER-001.md": (
            transcript_write("CAP-SLAM-KEYFRAME-DUAL-TRIGGER-001.md"),
            None,
        ),
        "06-产出/专利/主专利-SLAM-Token-交底书骨架.md": (
            transcript_write("主专利-SLAM-Token-交底书骨架.md"),
            None,
        ),
        "06-产出/论文/P1-弱网协同世界模型/meta.md": (
            transcript_write("P1-弱网协同世界模型/meta.md"),
            None,
        ),
        "06-产出/论文/P2-异构混编跨楼层/meta.md": (
            transcript_write("P2-异构混编跨楼层/meta.md"),
            None,
        ),
        "06-产出/论文/P3-关键帧压缩/meta.md": (
            transcript_write("P3-关键帧压缩/meta.md"),
            None,
        ),
        "04-文献阅读/notes/06-模型压缩-边缘部署/2025-IJCAI-BRCB-阅读笔记.md": (
            transcript_write("2025-IJCAI-BRCB-阅读笔记.md"),
            None,
        ),
    }


def transform_existing(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    new_content = apply_footer(content)
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main() -> None:
    restored: list[str] = []
    for rel, (body, meta_override) in restore_sources().items():
        path = ROOT / rel
        if not body.strip():
            print(f"SKIP restore (empty source): {rel}")
            continue
        parsed = extract_front_matter(body)
        if parsed:
            meta, body_only = parsed
        else:
            meta, body_only = meta_override or {}, body
        if meta_override:
            meta = meta_override
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body_only.rstrip() + format_footer(meta), encoding="utf-8")
        restored.append(rel)

    transformed: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = str(path.relative_to(ROOT))
        if rel in restored:
            continue
        if path.parts[0] in {".cursor", "SALM学习"}:
            continue
        if transform_existing(path):
            transformed.append(rel)

    print("Restored:", len(restored))
    for r in restored:
        print("  R", r)
    print("Transformed:", len(transformed))
    for t in transformed:
        print("  T", t)


if __name__ == "__main__":
    main()
