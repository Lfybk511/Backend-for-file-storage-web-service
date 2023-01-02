from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi import Depends, Query, Response
from fastapi.responses import JSONResponse
import iso8601
from fastapi.encoders import jsonable_encoder
from sql_app.model import models, schemas
from sql_app.utils.database import SessionLocal, engine
from sql_app.utils import crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/items/",
                      tags=["Стандартные функции"],
                      description="Добавление элементов файловой системы. При повторном добавлении элемент обновляется",
                      responses={
                          200: {"description": "Вставка или обновление прошли успешно."},
                          400: {"description": "Невалидная схема документа или входные данные не верны.",
                                "model": schemas.Error}
                      },)
def create_items(items: schemas.ItemImportRequest, db: Session = Depends(get_db)):
    crud.import_items(db, items)
    return Response(status_code=200)


@app.get("/get/item/{item_id}",
                     tags=["Стандартные функции"],
                     description="Получить информацию об элементе по ID.",
                     responses={
                         200: {"description": "Информация об элементе.",
                               "model": schemas.ItemGetNode},
                         400: {"description": "Невалидная схема документа или входные данные не верны.",
                               "model": schemas.Error},
                         404: {"description": "Элемент не найден.",
                               "model": schemas.Error}
                     },)
def get_items(item_id: str, db: Session = Depends(get_db)):
    item = crud.get_items_by_id(db, item_id)
    return item


@app.delete("/delete/items/{item_id}",
                        tags=["Стандартные функции"],
                        description="Удалить элемент по идентификатору. При удалении папки удаляются все дочерние элементы.",
                        responses={
                            200: {"description": "Элемент удален."},
                            400: {"description": "Невалидная схема документа или входные данные не верны.",
                                  "model": schemas.Error},
                            404: {"description": "Элемент не найден.",
                                  "model": schemas.Error}
                        },)
def delete_items(item_id: str, db: Session = Depends(get_db), date: str = Query(..., example="2023-01-02T14:14:06.516Z")):
    try:
        date = iso8601.parse_date(date)
    except ValueError:
        return JSONResponse(status_code=400, content=jsonable_encoder(schemas.Error(code=400, message="Validation time Failed")))
    item = crud.delete_item(db, item_id, date)
    return item

