from __future__ import annotations

import importlib

import tqdm
from httpx import Client
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from .check import Check
from .node import Node
from .rating import Issues
from .rule import Importance, Rule, Weights
from .stac_object import StacObject


class FunctionError(ImportError):
    """Raised when a function is mis-configured."""


class CheckResult(BaseModel):
    score: Annotated[float, Field(strict=True, ge=0, le=1)]
    message: str | None = Field(default=None)


class Rater:
    """Rate STAC objects"""

    def __init__(self, rules: dict[str, Rule], weights: Weights) -> None:
        self.checks = {}
        for id, rule in rules.items():
            parts = rule.function.split(":", 1)
            if len(parts) != 2:
                raise FunctionError(
                    f"invalid function syntax for rule '{id}': {rule.function}"
                )
            try:
                module = importlib.import_module(parts[0])
            except ImportError:
                raise FunctionError(f"missing module for rule '{id}': {parts[0]}")
            try:
                self.checks[id] = getattr(module, parts[1])
            except AttributeError:
                raise FunctionError(
                    f"missing function for rule '{id}' in module {parts[0]}: {parts[1]}"
                )

        self.rules = rules
        self.weights = weights

    def rate(
        self,
        stac_object: StacObject,
        *,
        rating: Rating | None = None,
        context: Context | None = None,
    ) -> Rating:
        if rating is None:
            rating = Rating(rules=self.rules, weights=self.weights)
        if context is None:
            context = Context()
        for id in self.rules.keys():
            if result := self.checks[id](context, stac_object):
                check = Check(score=result.score, message=result.message, rule_id=id)
                rating.add_check(check)
        rating.set(stac_object)
        return rating

    def rate_node(self, node: Node, context: Context | None = None) -> Rating:
        if context is None:
            context = Context()

        if node.is_catalog():
            progress_bar = tqdm.tqdm(
                total=(1 + len(node.children) + len(node.items)), desc=node.value.id
            )
        else:
            progress_bar = None

        rating = Rating(rules=self.rules, weights=self.weights)
        for child in node.children:
            child_rating = self.rate_node(child, context=context)
            rating.add_rating(child_rating)
            if progress_bar:
                progress_bar.update(1)
        for item in node.items:
            item_rating = self.rate(item, context=context)
            rating.add_rating(item_rating)
            if progress_bar:
                progress_bar.update(1)
        rating = self.rate(node.value, rating=rating, context=context)
        if progress_bar:
            progress_bar.update(1)
        return rating


class Context:
    def __init__(self) -> None:
        self._client = Client()
        self._response_cache: dict[str, str | None] = {}

    def get_error(self, url: str) -> None | str:
        if error := self._response_cache.get(url):
            return error
        else:
            try:
                response = self._client.get(url)
            except Exception as e:
                error = f"{url} errored on GET: {str(e)}"
            else:
                if response.is_error:
                    error = f"{url} errored on GET ({response.status_code})"
                else:
                    error = None
            self._response_cache[url] = error
            return error


class Rating:
    def __init__(self, rules: dict[str, Rule], weights: Weights):
        self._checks: list[Check] = []
        self._rules = rules
        self._weights = weights
        self.score: float = 0
        self.total: float = 0
        self._aggregate_score: float = 0
        self._aggregate_total: float = 0

    def get_stars(self) -> float:
        return 5 * self.aggregate_score / self.aggregate_total

    def add_check(self, check: Check) -> None:
        rule = self._rules[check.rule_id]
        if rule.importance == Importance.high:
            self.score += self._weights.high * check.score
            self.total += self._weights.high
        elif rule.importance == Importance.medium:
            self.score += self._weights.medium * check.score
            self.total += self._weights.medium
        elif rule.importance == Importance.low:
            self.score += self._weights.low * check.score
            self.total += self._weights.low
        else:
            raise Exception("unreachable")
        self._checks.append(check)

    def add_rating(self, rating: Rating) -> None:
        self._aggregate_score += rating.aggregate_score
        self._aggregate_total += rating.aggregate_total

    @property
    def aggregate_score(self) -> float:
        return self.score + self._aggregate_score

    @property
    def aggregate_total(self) -> float:
        return self.total + self._aggregate_total

    def get_issues(self) -> Issues:
        issues = Issues()
        for check in self._checks:
            if check.score < 1:
                rule = self._rules[check.rule_id]
                if rule.importance == Importance.high:
                    issues.high.append(check)
                elif rule.importance == Importance.medium:
                    issues.medium.append(check)
                elif rule.importance == Importance.low:
                    issues.low.append(check)
                else:
                    raise Exception("unreachable")
        return issues

    def set(self, stac_object: StacObject) -> None:
        from .rating import Rating

        rating = Rating(
            stars=self.get_stars(),
            issues=self.get_issues(),
            score=self.score,
            total=self.total,
        )
        if self._aggregate_score and self._aggregate_total:
            rating.aggregate_score = self.aggregate_score
            rating.aggregate_total = round(self.aggregate_total)

        stac_object.set_rating(rating)
