from sqlalchemy.orm import Session
from fastapi.exceptions import RequestValidationError
from sql_app.model import models, schemas
import sqlalchemy as sa
import logging
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def import_items(db: Session, items_request: schemas.ItemImportRequest):
    for item in items_request.items:
        parent_id = item.parent_id

        old_item = db.execute(sa.select(models.Item).where(models.Item.id == item.id))
        old_item = old_item.scalars().one_or_none()
        if old_item is not None:
            size_div = item.size - old_item.size
        else:
            size_div = item.size
        while parent_id is not None:
            parent = db.execute(sa.select(models.Item).where(models.Item.id == parent_id))
            parent = parent.scalars().one_or_none()

            if parent is not None:
                if parent.itemtype != "FOLDER":
                    db.rollback()
                    raise RequestValidationError(errors=[])

                parent.date = items_request.update_date
                parent.size = parent.size + size_div
                db.flush()

                parent_id = parent.parent_id
            else:
                break

        if old_item is not None:
            if old_item.itemtype != item.itemtype:
                db.rollback()
                raise RequestValidationError(errors=[])

            db.execute(sa.update(models.Item).where(models.Item.id == item.id)\
                                  .values(**item.dict(), date=items_request.update_date))
        else:
            new_item = models.Item(**item.dict(), date=items_request.update_date)
            db.add(new_item)
        db.flush()
        db.commit()


def get_items_by_id(db: Session, item_id: str):
    db_item = db.execute(sa.select(models.Item).where(models.Item.id == item_id))
    db_item = db_item.scalars().one_or_none()

    if db_item is None:
        return JSONResponse(status_code=404,
                            content=jsonable_encoder(schemas.Error(code=404, message="Not find item for ID")))

    return get_nodes_by_model(db, db_item)


def get_nodes_by_model(db: Session, db_item: models.Item):
    db_item_dict = db_item.indict()  # {key: value for (key, value) in db_item.items()}
    logging.debug(db_item_dict)
    item_node = schemas.ItemGetNode(**db_item_dict, children=None)

    if db_item.itemtype == "FILE":
        return item_node
    else:
        item_node.children = []
        children_objs = db.execute(sa.select(models.Item).where(models.Item.parent_id == db_item.id))
        children_objs = children_objs.scalars().all()

        for child in children_objs:
            item_node.children.append(get_nodes_by_model(db, child))

    return item_node


def delete_item(db: Session, item_id: str, date: datetime):
    """
    Delete item by id. May raise ItemNotFoundError
    """
    db_item = db.execute(sa.select(models.Item).where(models.Item.id == item_id))
    db_item = db_item.scalars().one_or_none()
    if db_item is not None:
        parent_id = db_item.parent_id
        child_size = delete_childs(db, item_id, 0)
    else:
        return JSONResponse(status_code=404,
                            content=jsonable_encoder(schemas.Error(code=404, message="Not find item for ID")))

    while parent_id is not None:
        parent = db.execute(sa.select(models.Item).where(models.Item.id == parent_id))
        parent = parent.scalars().one_or_none()

        parent.date = date
        parent.size = parent.size - child_size

        db.flush()
        parent_id = parent.parent_id
    db.commit()


def delete_childs(db: Session, item_id: str, size_child: int):
    db_items = db.execute(sa.select(models.Item).where(models.Item.parent_id == item_id))
    db_items = db_items.scalars().all()

    del_item = db.execute(sa.select(models.Item).where(models.Item.id == item_id))
    del_item = del_item.scalars().one_or_none()
    if del_item.itemtype != "FOLDER":
        size_child += del_item.size

    db.execute(sa.delete(models.Item).where(models.Item.id == item_id))
    db.flush()
    db.commit()
    for db_item in db_items:
        if db_item is not None:
            item_id = db_item.id
            size_child += delete_childs(db, item_id, 0)
    return size_child

