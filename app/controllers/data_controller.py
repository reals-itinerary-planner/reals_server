import logging
from typing import TypeVar, Type, List, Optional, Dict
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.query_schema import QueryParams
from app.core.database import get_async_db
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import DeclarativeMeta
from typing import Generic
from sqlalchemy import inspect, select

logger = logging.getLogger(__name__)

M = TypeVar("M", bound=DeclarativeMeta)


class DataController(Generic[M]):
    def __init__(self, model: Type[M], db: AsyncSession):
        self.model = model
        self.db = db
        self.repository = BaseRepository(model, db)
        # Get all valid relationship names for this model
        self.valid_relationships = [rel.key for rel in inspect(model).relationships]

    async def create(self, data_dict: dict) -> M:
        """Handle create request"""
        logger.info(f"Creating new {self.model.__name__} item")
        try:
            # Basic validation
            if not data_dict:
                raise HTTPException(
                    status_code=400, detail="Create data cannot be empty"
                )

            # Validate fields exist in model
            valid_fields = set(self.model.__mapper__.attrs.keys())
            invalid_fields = set(data_dict.keys()) - valid_fields
            if invalid_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid fields: {', '.join(invalid_fields)}",
                )

            # Delegate to repository
            try:
                result = await self.repository.create(data_dict)
                await self.db.refresh(result)
                return result
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    async def get_by_id(self, id: int, select: List[str] = None) -> M:
        try:
            # result = await self.repository.get_first(
            #     {"filter_by[uuid][equals]": id}, select
            # )
            result = await self.repository.get_by_id(id, select)
            if not result:
                raise HTTPException(status_code=404, detail="Record not found")
            return result
        except Exception as e:
            logger.error(f"Error getting item: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all(self, query_params: QueryParams) -> List[M]:
        """Get all records with pagination and filters"""
        try:

            result = await self.repository.get_all(
                page=query_params.page,
                items_per_page=query_params.items_per_page,
                order_by=query_params.order_by,
                order_type=query_params.order_type,
                filter_by=query_params.filter_by,
                # search_by=query_params.search_by,
                select_list=query_params.select,
                group_by=query_params.group_by,
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} items: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, id: str) -> bool:
        try:
            result = await self.repository.delete(id)
            if not result:
                raise HTTPException(status_code=404, detail="Record not found")
            return result
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update(self, id: str, data_dict: dict) -> M:
        """Update a record with nested relationships"""
        logger.info(f"Updating {self.model.__name__} with id {id}")

        try:

            result = await self.repository.update(id, data_dict)
            return result
        except Exception as e:
            await self.db.rollback()  # Ensure to rollback in case of an error
            raise e
