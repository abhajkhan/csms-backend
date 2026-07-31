"""Role-based access control (RBAC) FastAPI dependencies.

Provides ``RoleChecker`` — a callable dependency factory that enforces
minimum role requirements on protected endpoints.

Pre-built instances cover every combination used by the system design::

    require_admin               — admin only
    require_supervisor          — admin OR supervisor
    require_driver              — admin OR any driver type
    require_ajax_driver         — admin OR ajax driver
    require_hitachi_driver      — admin OR hitachi driver
    require_normal_driver       — admin OR normal driver
    require_admin_or_supervisor — admin OR supervisor (alias)

Usage::

    from app.dependencies.roles import require_admin, require_supervisor

    @router.post("/sites", status_code=201)
    async def create_site(
        current_user: CurrentUserResponse = Depends(require_admin),
        db: AsyncSession = Depends(get_db),
    ):
        ...

    @router.post("/attendance")
    async def mark_attendance(
        current_user: CurrentUserResponse = Depends(require_supervisor),
        db: AsyncSession = Depends(get_db),
    ):
        ...

Per 02_BACKEND_RULES.md §10 Authorization and
CSMS_SPEC.md §5 User Roles.
"""

from __future__ import annotations

from fastapi import Depends

from app.constants.enums import DriverType, UserRole
from app.core.exceptions import InsufficientRoleException
from app.dependencies.auth import get_current_active_user
from app.schemas.user import CurrentUserResponse


class RoleChecker:
    """Callable dependency factory that enforces role and driver-type access.

    When used as a FastAPI dependency, it returns the ``CurrentUserResponse``
    on success or raises ``InsufficientRoleException`` (403) on failure.

    Design:
        - ``allowed_roles`` lists the top-level ``UserRole`` values permitted.
        - ``allowed_driver_types`` (optional) further restricts *within* the
          ``DRIVER`` role.  When set, a user whose ``role == DRIVER`` must
          also have a ``driver_type`` in the allowed set.
        - Admin always passes role checks (they bypass driver-type checks too),
          matching the system design principle that admin can do everything.

    Args:
        allowed_roles:        Top-level roles that pass the check.
        allowed_driver_types: Optional driver sub-type restriction.

    Example — restrict to Ajax drivers only::

        require_ajax_driver = RoleChecker(
            allowed_roles=[UserRole.DRIVER],
            allowed_driver_types=[DriverType.AJAX],
        )
    """

    def __init__(
        self,
        allowed_roles: list[UserRole],
        allowed_driver_types: list[DriverType] | None = None,
    ) -> None:
        self._allowed_roles: frozenset[UserRole] = frozenset(allowed_roles)
        self._allowed_driver_types: frozenset[DriverType] | None = (
            frozenset(allowed_driver_types) if allowed_driver_types else None
        )

    async def __call__(
        self,
        current_user: CurrentUserResponse = Depends(get_current_active_user),
    ) -> CurrentUserResponse:
        """Enforce role and driver-type access.

        Args:
            current_user: Authenticated user from ``get_current_active_user``.

        Returns:
            The same ``CurrentUserResponse`` when access is permitted.

        Raises:
            ``InsufficientRoleException`` (403): When the user's role or
                                                  driver type is not allowed.
        """
        role: UserRole = current_user.role
        driver_type: DriverType | None = current_user.driver_type

        # Admins bypass all role checks (system-wide superuser).
        if role == UserRole.ADMIN:
            return current_user

        # Top-level role check.
        if role not in self._allowed_roles:
            raise InsufficientRoleException(
                [r.value for r in self._allowed_roles]
            )

        # Driver sub-type check (only applies when a restriction is set).
        if self._allowed_driver_types is not None:
            driver_type_denied = (
                role == UserRole.DRIVER
                and driver_type not in self._allowed_driver_types
            )
            if driver_type_denied:
                raise InsufficientRoleException(
                    [dt.value for dt in self._allowed_driver_types]
                )

        return current_user

    def __repr__(self) -> str:
        roles = ", ".join(r.value for r in self._allowed_roles)
        if self._allowed_driver_types:
            dt = ", ".join(d.value for d in self._allowed_driver_types)
            return f"RoleChecker(roles=[{roles}], driver_types=[{dt}])"
        return f"RoleChecker(roles=[{roles}])"


# ─── Pre-built dependency instances ──────────────────────────────────────────
# These are the canonical dependency objects used across all endpoint routers.
# Import and use them directly — do not instantiate RoleChecker ad-hoc.

#: Allows only admin accounts.
require_admin = RoleChecker(allowed_roles=[UserRole.ADMIN])

#: Allows admin or supervisor accounts.
require_supervisor = RoleChecker(
    allowed_roles=[UserRole.ADMIN, UserRole.SUPERVISOR]
)

#: Alias for ``require_supervisor`` (used in contexts where both roles apply).
require_admin_or_supervisor = require_supervisor

#: Allows admin or any driver (all sub-types).
require_driver = RoleChecker(
    allowed_roles=[UserRole.ADMIN, UserRole.DRIVER]
)

#: Allows admin or Ajax drivers specifically.
require_ajax_driver = RoleChecker(
    allowed_roles=[UserRole.ADMIN, UserRole.DRIVER],
    allowed_driver_types=[DriverType.AJAX],
)

#: Allows admin or Hitachi drivers specifically.
require_hitachi_driver = RoleChecker(
    allowed_roles=[UserRole.ADMIN, UserRole.DRIVER],
    allowed_driver_types=[DriverType.HITACHI],
)

#: Allows admin or Normal drivers specifically.
require_normal_driver = RoleChecker(
    allowed_roles=[UserRole.ADMIN, UserRole.DRIVER],
    allowed_driver_types=[DriverType.NORMAL],
)
