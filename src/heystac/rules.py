import logging
import urllib.parse
from typing import Any

import pystac.validation
import shapely
from pystac import STACObjectType
from pystac.errors import STACValidationError
from pystac.validation import JsonSchemaSTACValidator, RegisteredValidator

from .rate import CheckResult, Context
from .stac_object import StacObject

LINK_REL_TYPES_TO_CHECK = {
    "about",
    "alternate",
    "archives",
    "cite-as",
    "describedby",
    "docs",
    "documentation",
    "handbook",
    "help",
    "license",
    "preview",
    "related",
    "server",
    "source",
    "thumbnail",
    "via",
}


def validate_core(context: Context, stac_object: StacObject) -> CheckResult | None:
    data = stac_object.model_dump(mode="json", by_alias=True, exclude_none=True)
    try:
        pystac.validation.validate_dict(data, extensions=[])
    except STACValidationError as e:
        lines = str(e).splitlines()
        if lines:
            message = lines[0]
        else:
            message = None
        return CheckResult(score=0, message=message)
    else:
        return CheckResult(score=1)


def links(context: Context, stac_object: StacObject) -> CheckResult | None:
    total = 0
    score = 0
    messages = []
    for link in stac_object.links:
        url = urllib.parse.urlparse(link.href)
        if link.rel in LINK_REL_TYPES_TO_CHECK and url.scheme in ("http", "https"):
            total += 1
            error = context.get_error(link.href)
            if error:
                messages.append(str(error))
            else:
                score += 1
    if total == 0:
        return None
    else:
        return CheckResult(score=(score / total), message="\n".join(messages) or None)


def validate_geometry(context: Context, stac_object: StacObject) -> CheckResult | None:
    if stac_object.type == "Feature":
        assert stac_object.__pydantic_extra__
        try:
            geometry = stac_object.__pydantic_extra__["geometry"]
        except KeyError:
            return CheckResult(score=0, message="no geometry")
        try:
            geometry = shapely.geometry.shape(geometry)
        except Exception as e:
            return CheckResult(
                score=0, message=f"could not create shapely geometry: {e}"
            )
        if geometry.is_valid:
            return CheckResult(score=1)
        else:
            return CheckResult(score=0, message="invalid geometry")
    else:
        return None


class ExtensionOnlyValidator(JsonSchemaSTACValidator):
    def validate_core(
        self,
        stac_dict: dict[str, Any],
        stac_object_type: STACObjectType,
        stac_version: str,
        href: str | None = None,
    ) -> None:
        return None


EXTENSION_ONLY_VALIDATOR = ExtensionOnlyValidator()


def validate_extensions(
    context: Context, stac_object: StacObject
) -> CheckResult | None:
    data = stac_object.model_dump(mode="json", by_alias=True, exclude_none=True)
    old_validator = RegisteredValidator.get_validator()
    RegisteredValidator.set_validator(EXTENSION_ONLY_VALIDATOR)
    logging.disable()  # otherwise a failed schema fetch will be noisy
    message = ""
    total = 0
    score = 0
    try:
        logging.Logger.disabled = True
        for extension in stac_object.stac_extensions:
            total += 1
            try:
                pystac.validation.validate_dict(data, extensions=[extension])
            except Exception as e:
                lines = str(e).splitlines()  # Some jsonschema errors are wayy to big
                if lines:
                    message += lines[0]
            else:
                score += 1
    finally:
        RegisteredValidator.set_validator(old_validator)

    if total == 0:
        return None
    else:
        return CheckResult(score=(score / total), message=message or None)


def version(context: Context, stac_object: StacObject) -> CheckResult | None:
    if stac_object.stac_version in ("1.0.0", "1.1.0"):
        return CheckResult(score=1)
    else:
        return CheckResult(
            score=0,
            message=f"STAC version is not 1.0.0 or 1.1.0: {stac_object.stac_version}",
        )
