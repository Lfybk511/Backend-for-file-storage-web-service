from __future__ import annotations
from .models import ItemType
from pydantic import BaseModel, validator, root_validator, Field
from datetime import datetime
import iso8601


class ItemImport(BaseModel):
    id: str
    url: str | None = Field(default=None)
    parent_id: str | None = Field(default=None, alias="parentId")
    itemtype: ItemType = Field(..., alias="type")
    size: int | None = None

    class Config:
        schema_extra = {
            "example": {
                "id": "sfh-safsw-23d32-32df",
                "url": "/file/url1",
                "parentId": "fd3f2-dsf2-dsf2fd",
                "size": 256,
                "type": "FILE"
            }
        }
        validate_assignment = True

    @root_validator
    def validate_url(cls, values):
        if values['id'] is None:
            raise ValueError
        if (values['url'] is not None) and len(values['url']) > 255:
            raise ValueError
        if values['itemtype'] == 'FOLDER':
            if values['url'] is not None:
                raise ValueError
            if values['size'] is not None:
                raise ValueError
            else:
                values['size'] = 0
        if values['itemtype'] == 'FILE':
            if values['url'] is None:
                raise ValueError
            if values['size'] is None:
                raise ValueError
            else:
                if values['size'] <= 0:
                    raise ValueError
        return values


class ItemGetNode(BaseModel):
    id: str
    url: str | None = Field(default=None)
    parent_id: str | None = Field(default=None, alias="parentId")
    itemtype: ItemType = Field(..., alias="type")
    size: int | None
    date: datetime
    children: list[ItemGetNode] | None = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%SZ")
        }


class ItemImportRequest(BaseModel):
    items: list[ItemImport]
    update_date: datetime = Field(..., alias="updateDate")

    @validator('update_date', pre=True)
    def time_validate(cls, v):
        return iso8601.parse_date(v)

    class Config:
        schema_extra = {
            "example": {
                  "items": [
                    {
                      "type": "FOLDER",
                      "id": "FOLDER1",
                      "parentId": None
                    },
                    {
                      "type": "FILE",
                      "url": "/FOLDER1/url1",
                      "id": "FILE1",
                      "parentId": "FOLDER1",
                      "size": 200
                    },
                    {
                      "type": "FILE",
                      "url": "/FOLDER1/url2",
                      "id": "FILE12",
                      "parentId": "FOLDER1",
                      "size": 100
                    },
                    {
                      "type": "FOLDER",
                      "id": "FOLDER2",
                      "parentId": "FOLDER1"
                    },
                    {
                      "type": "FILE",
                      "url": "/FOLDER2/url2",
                      "id": "FILE21",
                      "parentId": "FOLDER2",
                      "size": 50
                    },
                    {
                      "type": "FOLDER",
                      "id": "FOLDER3",
                      "parentId": "FOLDER2"
                    },
                    {
                      "type": "FILE",
                      "url": "/FOLDER3/url2",
                      "id": "FILE31",
                      "parentId": "FOLDER3",
                      "size": 10
                    }
                  ],
                  "updateDate": "2022-12-02T12:00:00Z"
                }
        }


class Error(BaseModel):
    code: int
    message: str

    class Config:
        schema_extra = {
            "example": {
                "code": "400",
                "message": "Validation Failed"
            }
        }


# Because we refer to the class within the class
ItemGetNode.update_forward_refs()

