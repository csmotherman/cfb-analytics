from __future__ import annotations

from dataclasses import dataclass, field


class ValidationError(ValueError):
    pass


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)

    def warn(self, condition: bool, message: str) -> None:
        if not condition:
            self.warnings.append(message)

    def raise_for_errors(self) -> None:
        if self.errors:
            raise ValidationError("Validation failed:\n- " + "\n- ".join(self.errors))
