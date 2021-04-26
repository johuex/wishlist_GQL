from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date, DateTime, Enum
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from .database import Base, engine
from enum import Enum as PyEnum


class RoleEnum(PyEnum):
    GUEST = 0
    ORGANIZER = 1
    FRIENDS = 2


class DegreeEnum(PyEnum):
    NOTWANT = 0
    WANT = 1
    REALLYWANT = 2
    NOTSTATED = 3


class AccessLevelEnum(PyEnum):
    ALL = 0
    FRIENDS = 1
    NOBODY = 2


class StatusEnum(PyEnum):
    FREE = 0
    RESERVED = 1
    PERFORMED = 2


access_level = ENUM(AccessLevelEnum, name="access")
degree = ENUM(DegreeEnum, name="degree")
role = ENUM(RoleEnum, name="role")
status = ENUM(StatusEnum, name="status")


class FriendRequests(Base):
    __tablename__ = "friends_requests"
    user_id_from = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user_id_to = Column(Integer, ForeignKey("users.id"), primary_key=True)


class FriendShip(Base):
    __tablename__ = "friendship"
    user_id_1 = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user_id_2 = Column(Integer, ForeignKey("users.id"), primary_key=True)


class User(Base):
    __tablename__ = 'users'
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    phone_number = Column(String(15), unique=True)
    user_name = Column(String(128), nullable=False)
    surname = Column(String(128))
    userpic = Column(Text())
    about = Column(String(1000))
    birthday = Column(Date())
    password_hash = Column(Text())
    nickname = Column(String(128))
    email = Column(String(255), nullable=False, unique=True)
    last_seen = Column(DateTime())
    token = Column(Text())
    refresh_token = Column(Text())
    user_lists = relationship("Wishlist", cascade="all,delete", foreign_keys="Wishlist.user_id")
    # TODO написать им резольверы
    friend_requests = relationship("FriendRequests", cascade="all,delete", foreign_keys="FriendRequests.user_id_from")
    friends = relationship("FriendShip", cascade="all,delete", foreign_keys="FriendShip.user_id_1")
    items_owner = relationship("Item", cascade="all,delete", foreign_keys="Item.owner_id")
    items_giver = relationship("Item", cascade="all", foreign_keys="Item.giver_id")
    groups = relationship("GroupUser", cascade="all,delete", foreign_keys="GroupUser.user_id")


class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    about = Column(String(1000))
    access_level = Column(access_level, nullable=False)
    items = relationship("Item", foreign_keys="Item.list_id")
    user_owner = relationship("User", foreign_keys=[user_id])


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    about = Column(String(1000))
    access_level = Column(access_level, nullable=False)
    status = Column(status, nullable=False)
    giver_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    date_creation = Column(DateTime(), nullable=False)
    list_id = Column(Integer, ForeignKey('wishlist.id'))
    date_for_status = Column(DateTime(), nullable=False)
    degree = Column(degree)
    giver = relationship("User", foreign_keys=[giver_id])
    owner = relationship("User", foreign_keys=[owner_id])
    pictures = relationship("ItemPicture", cascade="all,delete", foreign_keys="ItemPicture.item_id")
    in_wishlist = relationship("Wishlist", foreign_keys=[list_id])


class ItemPicture(Base):
    __tablename__ = "item_picture"
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    path_to_picture = Column(Text(), primary_key=True)


class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    about = Column(String(1000))
    access_level = Column(access_level, nullable=False)
    date_creation = Column(DateTime(), nullable=False)
    date = Column(DateTime(), nullable=False)
    users = relationship("GroupUser", cascade="all,delete", foreign_keys="GroupUser.group_id")
    items = relationship("ItemGroup", cascade="all,delete", foreign_keys="ItemGroup.group_id")
    lists = relationship("GroupList", cascade="all,delete", foreign_keys="GroupList.group_id")


class GroupList(Base):
    __tablename__ = "group_list"
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    wishlist_id = Column(Integer, ForeignKey('wishlist.id'), primary_key=True)
    group = relationship("Group", foreign_keys=[group_id])
    lists = relationship("Wishlist", cascade="all,delete", foreign_keys=[wishlist_id])


class ItemGroup(Base):
    __tablename__ = "item_group"
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    group = relationship("Group", foreign_keys=[group_id])
    item = relationship("Item", cascade="all,delete", foreign_keys=[item_id])


class GroupUser(Base):
    __tablename__ = "group_user"
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_in_group = Column(role, nullable=False)
    users = relationship("User", foreign_keys=[user_id])
    groups = relationship("Group", foreign_keys=[group_id])


Base.metadata.create_all(engine)
