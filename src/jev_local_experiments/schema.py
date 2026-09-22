"""Validation for the shared typed-decision benchmark contract."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a benchmark case does not follow the workspace contract."""


@dataclass(frozen=True)
class Question:
    kind: str
    instructions: Any
    criteria: Mapping[str, str] | tuple[str, ...] | None


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    state: Any
    questions: dict[str, Question]
    labels: dict[str, Any]


_QUESTION_TYPES = {"noul", "choice", "score"}


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{name} must be an object")
    return value


def _require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")
    return value


def validate_case(raw: Mapping[str, Any]) -> BenchmarkCase:
    """Validate and normalize one JSON-compatible benchmark case."""

    case = _require_mapping(raw, "case")
    case_id = _require_text(case.get("id"), "id")
    if "state" not in case:
        raise ValidationError(f"case {case_id!r} is missing state")

    raw_questions = _require_mapping(case.get("questions"), f"case {case_id!r}.questions")
    if not raw_questions:
        raise ValidationError(f"case {case_id!r}.questions must not be empty")

    questions: dict[str, Question] = {}
    for question_id, raw_question in raw_questions.items():
        question_name = _require_text(question_id, "question id")
        question = _require_mapping(raw_question, f"question {question_name!r}")
        kind = _require_text(question.get("type"), f"question {question_name!r}.type")
        if kind not in _QUESTION_TYPES:
            allowed = ", ".join(sorted(_QUESTION_TYPES))
            raise ValidationError(f"question {question_name!r}.type must be one of: {allowed}")
        instructions = question.get("instructions")
        if instructions is None:
            raise ValidationError(f"question {question_name!r} is missing instructions")

        criteria: Mapping[str, str] | tuple[str, ...] | None
        if kind == "choice":
            raw_criteria = _require_mapping(
                question.get("criteria"), f"question {question_name!r}.criteria"
            )
            if not raw_criteria:
                raise ValidationError(f"question {question_name!r}.criteria must not be empty")
            normalized_choice: dict[str, str] = {}
            for option, description in raw_criteria.items():
                option_name = _require_text(option, f"question {question_name!r} option")
                if description is None:
                    normalized_choice[option_name] = ""
                elif isinstance(description, str):
                    normalized_choice[option_name] = description
                else:
                    raise ValidationError(
                        f"question {question_name!r} option {option_name!r} description must be text or null"
                    )
            criteria = normalized_choice
        elif kind == "score":
            raw_criteria = question.get("criteria")
            if not isinstance(raw_criteria, (list, tuple)) or len(raw_criteria) < 2:
                raise ValidationError(
                    f"question {question_name!r}.criteria must contain at least two levels"
                )
            levels = tuple(
                _require_text(level, f"question {question_name!r} score level")
                for level in raw_criteria
            )
            criteria = levels
        else:
            criteria = None

        questions[question_name] = Question(kind=kind, instructions=instructions, criteria=criteria)

    raw_labels = case.get("labels", {})
    labels = dict(_require_mapping(raw_labels, f"case {case_id!r}.labels"))
    for question_id, label in labels.items():
        if question_id not in questions:
            raise ValidationError(f"label {question_id!r} has no matching question")
        question = questions[question_id]
        if question.kind == "noul":
            if type(label) is not bool:
                raise ValidationError(f"label for {question_id!r} must be a boolean")
        elif question.kind == "choice":
            assert isinstance(question.criteria, Mapping)
            if not isinstance(label, str) or label not in question.criteria:
                raise ValidationError(f"label for {question_id!r} must name one of its criteria")
        else:
            assert isinstance(question.criteria, tuple)
            if type(label) is not int or not 0 <= label < len(question.criteria):
                raise ValidationError(f"label for {question_id!r} must be a valid zero-based score index")

    return BenchmarkCase(case_id=case_id, state=case["state"], questions=questions, labels=labels)


def load_suite(path: str | Path) -> list[BenchmarkCase]:
    """Load and validate a JSONL benchmark suite, rejecting duplicate ids."""

    suite_path = Path(path)
    if not suite_path.is_file():
        raise ValidationError(f"benchmark file does not exist: {suite_path}")

    cases: list[BenchmarkCase] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(suite_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"line {line_number} is not valid JSON: {exc.msg}") from exc
        try:
            case = validate_case(raw)
        except ValidationError as exc:
            raise ValidationError(f"line {line_number}: {exc}") from exc
        if case.case_id in seen_ids:
            raise ValidationError(f"duplicate case id: {case.case_id!r}")
        seen_ids.add(case.case_id)
        cases.append(case)
    if not cases:
        raise ValidationError(f"benchmark file contains no cases: {suite_path}")
    return cases
