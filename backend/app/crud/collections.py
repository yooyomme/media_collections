
import uuid
from fastapi import HTTPException

from sqlalchemy import Select, and_, Update, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app import security
from app.loggers import debug_logger
from app.models import Collection, User, MediaItemCollection
from app.models.associations import CollectionMember, Vote
from app.schemas.collections import CollectionCreateSchema, CollectionSettingsUpdateSchema
from app.schemas.votes import VoteBaseSchema, VoteCreateSchema


async def get_collections(db: AsyncSession):
    try:
        collections_list = await db.execute(
            Select(Collection)
            .options(selectinload(Collection.item_associations)
                     .joinedload(MediaItemCollection.media_item))
        )
        return collections_list.scalars().all()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Collections not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_collections_by_author(db: AsyncSession, user_id: uuid.UUID):
    try:
        uid = str(user_id)
        collections_list = await db.execute(Select(Collection).where(Collection.user_id == uid)
                                            .options(selectinload(Collection.item_associations)
                                                     .joinedload(MediaItemCollection.media_item))
                                            )
        return collections_list.scalars().all()
    except Exception as e:
        debug_logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

async def get_membership_collections_for_user(db: AsyncSession, user_id: uuid.UUID):
    try:
        uid = str(user_id)
        collections_list = await db.execute(
            Select(Collection).where(Collection.memberships.any(CollectionMember.user_id == uid))
            .options(selectinload(Collection.item_associations)
                     .joinedload(MediaItemCollection.media_item))
        )
        return collections_list.scalars().all()
    except Exception as e:
        debug_logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


async def get_collection(db: AsyncSession, collection_id: uuid.UUID):
    try:
        col_id = str(collection_id)
        collection_data = await db.execute(Select(Collection).where(Collection.id == col_id)
                                           .options(selectinload(Collection.item_associations)
                                                    .joinedload(MediaItemCollection.media_item))
                                           )
        collection = collection_data.scalars().first()
        return collection
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Collection not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_collection(db: AsyncSession, collection_data: CollectionCreateSchema, user: User):
    try:
        data_for_dump = collection_data.model_dump()
        collection = Collection(**data_for_dump)
        db.add(collection)
        await db.commit()
        await db.refresh(collection)
        collection_for_return = await db.execute(Select(Collection)
                                                 .where(Collection.id == collection.id)
                                                 .options(selectinload(Collection.item_associations).joinedload(MediaItemCollection.media_item))
                                                 )
        return collection_for_return.scalar_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_collection(db: AsyncSession, collection_id: uuid.UUID, collection_data: CollectionCreateSchema):
    try:
        col_id = str(collection_id)
        existing_collection = await db.execute(
            Select(Collection)
            .where(Collection.id == col_id)
            .options(selectinload(Collection.item_associations)
                     .joinedload(MediaItemCollection.media_item))
        )
        collection_for_update = existing_collection.scalar_one()
        data_for_update = collection_data.model_dump(exclude_unset=True, exclude={"user_id"})
        for key, value in data_for_update.items():
            if (key == "title") and (value == "" or value.strip() == ""):  # если title из одних пробелов или пустой, заменяем на Коллекция
                value = "Коллекция"
            setattr(collection_for_update, key, value)
        await db.commit()
        await db.refresh(collection_for_update)
        return collection_for_update
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Media items not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_collection(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        existing_collection = await db.execute(Select(Collection).where(Collection.id == col_id))
        item = existing_collection.scalar_one()
        await db.delete(item)
        await db.commit()
        return True
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Collection does not exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def find_item_in_collection(db: AsyncSession, collection_id: uuid.UUID, item_id: int):
    try:
        col_id = str(collection_id)
        item_exists = await db.execute(
            Select(MediaItemCollection).where(and_(
                MediaItemCollection.collection_id == col_id,
                MediaItemCollection.media_item_id == item_id
            ))
        )
        result = item_exists.scalar_one_or_none()
        if result:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def set_cover(db: AsyncSession, collection_id: uuid.UUID, cover_url: str):
    try:
        col_id = str(collection_id)
        collection_to_update = await db.execute(Select(Collection).where(Collection.id == col_id)
                                                .options(selectinload(Collection.item_associations)
                                                         .joinedload(MediaItemCollection.media_item)))
        collection = collection_to_update.scalar_one_or_none()
        if collection:
            collection.cover_image = cover_url
            await db.commit()
            await db.refresh(collection)
        result = await db.execute(
            Select(Collection).where(Collection.id == col_id)
            .options(selectinload(Collection.item_associations)
                     .joinedload(MediaItemCollection.media_item))
        )
        rs = result.scalar_one()
        return rs
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Collection not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_cover(db: AsyncSession, collection_id: uuid.UUID):
    try:
        col_id = str(collection_id)
        await db.execute(Update(Collection).where(Collection.id == col_id).values(cover_image=None))
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_item_rating(db: AsyncSession, vote_data: VoteCreateSchema):
    try:
        col_id = str(vote_data.collection_id)
        item_id = vote_data.item_id
        vote_stats = await db.execute(Select(
            func.avg(Vote.score).label("average_score"),
            func.count(Vote.id).label("number_of_votes")
        ).where(and_(
            Vote.collection_id == col_id, Vote.item_id == item_id
        )))
        stats = vote_stats.one()
        if stats.average_score:
            avg_score = float(stats.average_score)
            vote_count = int(stats.number_of_votes)
            await db.execute(
                Update(MediaItemCollection).where(and_(
                    MediaItemCollection.collection_id == col_id,
                    MediaItemCollection.media_item_id == item_id)).values(average_rating=avg_score, votes_count=vote_count)
            )
            await db.commit()
        result = await db.execute(Select(MediaItemCollection).where(and_(
            MediaItemCollection.collection_id == col_id,
            MediaItemCollection.media_item_id==item_id)))
        res_item = result.scalar_one()
        res_item.user_rate = vote_data.score
        return res_item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_item_in_collection_statistics(db: AsyncSession, data: VoteBaseSchema, user: User):
    try:
        data_for_dump = data.model_dump()
        col_id = str(data_for_dump.collection_id)
        item_id = data_for_dump.item_id
        uid = str(user.id)
        item_in_collection = await db.execute(Select(MediaItemCollection).where(MediaItemCollection.collection_id == col_id))
        item = item_in_collection.scalar_one()

        item_rating_info = await db.execute(Select(Vote).where(and_(
            Vote.collection_id == col_id,
            Vote.item_id == item_id,
            Vote.user_id ==uid)))
        rating_info = item_rating_info.scalar_one_or_none()
        if rating_info:
            user_rate = rating_info.score
        else:
            user_rate = 0
        return {
            "item_id": item_id,
            "collection_id": col_id,
            "user_rate": user_rate,
            "average_rating": item.average_rating,
            "votes_count": item.votes_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def set_vote_for_item_in_collection(db: AsyncSession, data: VoteCreateSchema, user: User):
    try:
        data_for_dump = data.model_dump()
        uid = str(user.id)
        col_id = str(data.collection_id)
        item_id = data.item_id
        vote_already_exists = await db.execute(Select(Vote).where(and_(
                Vote.collection_id == col_id,
                Vote.item_id == item_id,
                Vote.user_id == uid)))
        existing_vote = vote_already_exists.scalar_one_or_none()
        if existing_vote:
            existing_vote.score = data.score
            await db.commit()
            await db.refresh(existing_vote)
        else:
            vote = Vote(
                **data_for_dump,
                user_id=uid,
            )
            db.add(vote)
            await db.commit()
            await db.refresh(vote)
        result = await db.execute(Select(Vote).where(and_(Vote.collection_id == col_id,
                                                          Vote.item_id == item_id,
                                                          Vote.user_id == uid)))
        return result.scalar_one()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def remove_vote_for_item_in_collection(db: AsyncSession, data: VoteBaseSchema, user: User):
    try:
        data_for_dump = data.model_dump()
        col_id = str(data_for_dump.collection_id)
        item_id = data_for_dump.item_id
        uid = str(user.id)
        existing_vote = await db.execute(Select(Vote).where(and_(
            Vote.collection_id == col_id, Vote.item_id == item_id, Vote.user_id == uid)))
        vote = existing_vote.scalar_one_or_none()
        if vote:
            await db.delete(vote)
            await db.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_rating_info_in_collection(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        uid = str(user.id)
        data = {}
        vote_data = await db.execute(Select(Vote).where(and_(Vote.collection_id == col_id, Vote.user_id == uid)))
        vote = vote_data.scalars().all()
        if not vote:
            return data
        for item in vote:
            data[item.item_id] = item.score
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_all_collection_members(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        existing_collection = await db.execute(
            Select(CollectionMember).where(CollectionMember.collection_id == col_id)
            .options(joinedload(CollectionMember.user))
        )
        collection_members = existing_collection.scalars().all()
        return collection_members
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def find_collection_member_or_owner(db: AsyncSession, collection_id: uuid.UUID, member: User):
    try:
        col_id = str(collection_id)
        member_id = str(member.id)
        existing_member = await db.execute(
            Select(CollectionMember).where(and_(
                CollectionMember.collection_id == col_id, CollectionMember.user_id == member_id,
            ))
        )
        member = existing_member.scalar_one_or_none()
        if member:
            return True

        existing_owner = await db.execute(
            Select(Collection).where(and_(
                Collection.id == col_id, Collection.user_id == member_id
            ))
        )
        owner = existing_owner.scalar_one_or_none()
        if owner:
            return True

        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def set_user_for_collection_member(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        uid = str(user.id)
        member = CollectionMember(
            collection_id=col_id,
            user_id=uid,
        )
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def reset_all_collection_members(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        uid = str(user.id)
        existing_collection_members = await db.execute(
            Select(CollectionMember).where(CollectionMember.collection_id == col_id)
        )
        collection_members = existing_collection_members.scalars().all()
        for member in collection_members:
            await db.delete(member)
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def reset_one_member(db: AsyncSession, collection_id: uuid.UUID, member_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        uid = str(user.id)
        member_id = str(member_id)
        existing_collection_member = await db.execute(
            Select(CollectionMember).where(and_(CollectionMember.collection_id == col_id,
                                                CollectionMember.user_id==member_id))
        )
        collection_member = existing_collection_member.scalar_one_or_none()
        if collection_member:
            await db.delete(collection_member)
        await db.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def update_collection_privacy_settings(db: AsyncSession, collection_id: uuid.UUID, settings: CollectionSettingsUpdateSchema, user: User):
    try:
        col_id = str(collection_id)
        uid = str(user.id)
        existing_collection = await db.execute(
            Select(Collection).where(and_(
                Collection.id == col_id, Collection.user_id == uid
            )).options(selectinload(Collection.item_associations)
                       .joinedload(MediaItemCollection.media_item))
        )
        collection = existing_collection.scalar_one_or_none()
        if collection:
            data_for_update = {}
            if settings.access_type:
                data_for_update["access_type"] = settings.access_type
            if settings.password:
                data_for_update["password_hash"] = security.get_password_hash(settings.password)

            for key, value in data_for_update.items():
                setattr(collection, key, value)
            await db.commit()
            await db.refresh(collection)
            nw_collection = await db.execute(
                Select(Collection).where(and_(
                Collection.id == col_id, Collection.user_id == uid
            )).options(selectinload(Collection.item_associations)
                          .joinedload(MediaItemCollection.media_item))
            )
            collection = nw_collection.scalar_one_or_none()
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_invite_token(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        uid = str(user.id)
        existing_collection = await db.execute(
            Select(Collection).where(and_(
                Collection.id == col_id, Collection.user_id == uid,
            ))
        )
        collection = existing_collection.scalar_one_or_none()
        if collection:
            if collection.invite_token is None:
                new_invite_token = str(uuid.uuid4())
                setattr(collection, "invite_token", new_invite_token)
                await db.commit()
                await db.refresh(collection)
            return collection.invite_token
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def reset_invite_token(db: AsyncSession, collection_id: uuid.UUID, user: User):
    try:
        col_id = str(collection_id)
        uid = str(user.id)
        existing_collection = await db.execute(
            Select(Collection).where(and_(
                Collection.user_id == uid,
                Collection.id == col_id,
            ))
        )
        collection = existing_collection.scalar_one_or_none()
        if collection:
            new_access_token = str(uuid.uuid4())
            collection.invite_token = new_access_token
            await db.commit()
            await db.refresh(collection)
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))