"""Rule-based planner for converting language instructions into drone actions."""

from __future__ import annotations

import re
from typing import Any

from cosmos_vla_drone.baseline.safety import assert_plan_safe
from cosmos_vla_drone.baseline.schema import validate_plan


COLOR_ALIASES = {
    "red": ("red", "red target", "红", "红色", "红色目标"),
    "blue": ("blue", "blue target", "蓝", "蓝色", "蓝色目标"),
    "green": ("green", "green target", "绿", "绿色", "绿色目标"),
}

UNSUPPORTED_CHINESE_COLOR_PATTERN = re.compile(r"([\u4e00-\u9fff]{1,3})色目标")
UNSUPPORTED_ENGLISH_COLOR_PATTERN = re.compile(r"\b([a-z]+)\s+(?:target|object|goal)\b")

DEFAULT_TAKEOFF_ALTITUDE = 1.5
DEFAULT_MOVE_ABOVE_HEIGHT = 1.0
DEFAULT_HOVER_DURATION = 5.0


def normalize_instruction(instruction: str) -> str:
    """Normalize instruction text for simple rule matching."""

    return instruction.strip().lower()


def extract_color(text: str) -> str | None:
    """Extract a supported target color from Chinese or English instruction text."""

    for color, aliases in COLOR_ALIASES.items():
        if any(alias in text for alias in aliases):
            return color
    return None


def detect_unsupported_color_query(text: str) -> str | None:
    """Detect target-color expressions outside the supported color set."""

    if extract_color(text) is not None:
        return None

    chinese_match = UNSUPPORTED_CHINESE_COLOR_PATTERN.search(text)
    if chinese_match:
        return chinese_match.group(1) + "色"

    english_match = UNSUPPORTED_ENGLISH_COLOR_PATTERN.search(text)
    if english_match:
        candidate = english_match.group(1)
        non_color_words = {"the", "a", "an", "colored", "colour", "color"}
        if candidate not in non_color_words:
            return candidate

    return None


def extract_first_number_before_keywords(
    text: str,
    keywords: tuple[str, ...],
    default: float,
) -> float:
    """Extract a nearby numeric value before or after task-specific keywords."""

    unit_pattern = r"(?:米|m|meter|meters|秒|s|sec|second|seconds)?"

    for keyword in keywords:
        patterns = [
            rf"(\d+(?:\.\d+)?)\s*{unit_pattern}\s*{re.escape(keyword)}",
            rf"{re.escape(keyword)}\s*(\d+(?:\.\d+)?)\s*{unit_pattern}",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))

    return default


def extract_move_to_position(text: str) -> tuple[float, float, float] | None:
    """Extract a move_to position from x/y/z coordinate expressions."""

    patterns = [
        r"x\s*=\s*(-?\d+(?:\.\d+)?)\s*,?\s*y\s*=\s*(-?\d+(?:\.\d+)?)\s*,?\s*z\s*=\s*(-?\d+(?:\.\d+)?)",
        r"x\s*(-?\d+(?:\.\d+)?)\s*,?\s*y\s*(-?\d+(?:\.\d+)?)\s*,?\s*z\s*(-?\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return (
                float(match.group(1)),
                float(match.group(2)),
                float(match.group(3)),
            )

    return None


def parse_instruction(instruction: str) -> list[dict[str, Any]]:
    """Parse a natural language instruction into a validated action list."""

    text = normalize_instruction(instruction)
    unsupported_color = detect_unsupported_color_query(text)
    if unsupported_color is not None:
        raise ValueError(f"unsupported target color: {unsupported_color}")

    color = extract_color(text)
    actions: list[dict[str, Any]] = []

    if _contains_any(text, ("起飞", "takeoff", "take off")):
        altitude = extract_first_number_before_keywords(
            text,
            ("起飞", "takeoff", "take off"),
            DEFAULT_TAKEOFF_ALTITUDE,
        )
        actions.append({"action": "takeoff", "altitude": altitude})

    if color is not None and _contains_any(text, ("找", "找到", "寻找", "搜索", "search", "find")):
        actions.append({"action": "search", "target": color})

    move_to_position = extract_move_to_position(text)
    if move_to_position is not None and _contains_any(text, ("move to", "飞到", "移动到")):
        actions.append({"action": "move_to", "position": move_to_position})

    if color is not None and _contains_any(text, ("上方", "above")):
        height = extract_first_number_before_keywords(
            text,
            ("上方", "above"),
            DEFAULT_MOVE_ABOVE_HEIGHT,
        )
        actions.append({"action": "move_above", "target": color, "height": height})

    if _contains_any(text, ("悬停", "hover")):
        duration = extract_first_number_before_keywords(
            text,
            ("悬停", "hover"),
            DEFAULT_HOVER_DURATION,
        )
        actions.append({"action": "hover", "duration": duration})

    if _contains_any(text, ("降落", "着陆", "land")):
        actions.append({"action": "land"})

    if not actions:
        raise ValueError(f"Could not parse instruction into actions: {instruction}")

    validated_actions = validate_plan(actions)
    assert_plan_safe(validated_actions)
    return validated_actions


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)
