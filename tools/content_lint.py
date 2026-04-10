from __future__ import annotations

import re

from levels_data import GLOSSARY, LEVELS


STOP_WORDS = {"ошибка пользователя", "ты не понимаешь", "провал"}


def run_content_lint() -> list[str]:
    issues: list[str] = []
    for level in LEVELS:
        if not level.get("rules"):
            issues.append(f"Level {level['id']} has no rules")
        text_blob = " ".join([level.get("wisdom", ""), level.get("mission", "")]).lower()
        for bad in STOP_WORDS:
            if bad in text_blob:
                issues.append(f"Level {level['id']} contains stop-phrase: {bad}")
        for rule in level.get("rules", []):
            if not rule.get("label"):
                issues.append(f"Level {level['id']} rule {rule.get('id')} has no label")

    # glossary coverage for known core terms appearing in content
    content = " ".join([lvl["wisdom"] + " " + lvl["mission"] for lvl in LEVELS]).lower()
    seen_terms = set(re.findall(r"[a-zA-Z_]+", content))
    required = {"if", "for", "string", "int", "bool"}
    for term in required:
        if term in seen_terms and term not in GLOSSARY:
            issues.append(f"Glossary missing term: {term}")

    return issues


if __name__ == "__main__":
    found = run_content_lint()
    if found:
        for issue in found:
            print(issue)
        raise SystemExit(1)
    print("content_lint: OK")
