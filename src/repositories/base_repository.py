"""Base repository with common CRUD operations."""

from typing import Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository for common database operations."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        """Initialize repository.

        Args:
            session: Async database session.
            model: SQLAlchemy model class.
        """
        self.session = session
        self.model = model

    async def create(self, entity: T) -> T:
        """Create a new entity.

        Args:
            entity: Entity to create.

        Returns:
            Created entity with ID.
        """
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Entity if found, None otherwise.
        """
        return await self.session.get(self.model, entity_id)

    async def get_all(self) -> Sequence[T]:
        """Get all entities.

        Returns:
            List of all entities.
        """
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def update(self, entity: T) -> T:
        """Update an entity.

        Args:
            entity: Entity to update.

        Returns:
            Updated entity.
        """
        merged = await self.session.merge(entity)
        await self.session.flush()
        return merged

    async def delete(self, entity: T) -> None:
        """Delete an entity.

        Args:
            entity: Entity to delete.
        """
        await self.session.delete(entity)
        await self.session.flush()

    async def delete_by_id(self, entity_id: int) -> bool:
        """Delete entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            True if deleted, False if not found.
        """
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.delete(entity)
            return True
        return False

    async def exists(self, entity_id: int) -> bool:
        """Check if entity exists.

        Args:
            entity_id: Entity ID.

        Returns:
            True if exists, False otherwise.
        """
        entity = await self.get_by_id(entity_id)
        return entity is not None

    async def count(self) -> int:
        """Count all entities.

        Returns:
            Total count of entities.
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0
