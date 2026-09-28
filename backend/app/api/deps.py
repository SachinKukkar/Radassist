from collections.abc import Mapping
from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings
from app.services.health import DEPENDENCY_CHECKS, DependencyCheck


def get_app_settings(request: Request) -> Settings:
    """Return the Settings instance the app was created with."""
    settings: Settings = request.app.state.settings
    return settings


def get_dependency_checks() -> Mapping[str, DependencyCheck]:
    """Return the readiness checks to run. Tests override this dependency with fakes."""
    return DEPENDENCY_CHECKS


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
DependencyChecksDep = Annotated[Mapping[str, DependencyCheck], Depends(get_dependency_checks)]
