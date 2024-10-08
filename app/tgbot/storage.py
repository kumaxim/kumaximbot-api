import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, Optional
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from sqlalchemy import delete, update, select

from app.db.models import StorageFSM


class SQLAlchemyStorage(BaseStorage):
    def __init__(self, session: AsyncSession) -> None:
        self.__session__: AsyncSession = session

    async def close(self) -> None:
        """Close the storage.

        Don't need to implement this method, because connection manage by sqlalchemy
        """
        pass

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        if state is None:
            await self.__session__.execute(delete(StorageFSM).filter_by(**key.__dict__))
        else:
            storage = await self.__session__.scalar(select(StorageFSM).filter_by(**key.__dict__))

            if storage:
                await self.__session__.execute(
                    update(StorageFSM)
                    .filter_by(**key.__dict__)
                    .values(state=state.state if isinstance(state, State) else state)
                )
            else:
                self.__session__.add(
                    StorageFSM(**key.__dict__, state=state.state if isinstance(state, State) else state)
                )

        await self.__session__.commit()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        state = await self.__session__.scalar(select(StorageFSM).filter_by(**key.__dict__))

        return state.state if state and state.state else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        storage = await self.__session__.scalar(select(StorageFSM).filter_by(**key.__dict__))

        if storage:
            await self.__session__.execute(update(StorageFSM).filter_by(**key.__dict__).values(data=json.dumps(data)))

        if not storage and data.keys():
            self.__session__.add(StorageFSM(**key.__dict__, data=json.dumps(data)))

        await self.__session__.commit()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        storage = await self.__session__.scalar(select(StorageFSM).filter_by(**key.__dict__))

        return json.loads(storage.data) if storage and storage.data else {}
