from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint, Integer, String, Text, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base, engine


RoleEnum = Enum('GUEST', 'ORGANIZER', 'FRIENDS', name = "role")

DegreeEnum = Enum('NOTWANT', 'WANT', 'REALLYWANT', name = "degree")

AccessLevelEnum = Enum('ALL', 'FRIENDS', 'NOBODY', name = "access")

StatusEnum = Enum('FREE', 'RESERVED', 'PERFORMED', name = "status")


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
    '''id = Column(
        Integer,
        ForeignKey('friendship.user_id_1'),
        ForeignKey('friendship.user_id_2'),
        ForeignKey('friends_requests.user_id_from'),
        ForeignKey('friends_requests.user_id_to'),
        primary_key=True,
        autoincrement=True
    )'''
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
    token_experation = Column(DateTime())
    user_lists = relationship("Wishlist")
    friends_to = relationship("FriendRequests", foreign_keys="FriendRequests.user_id_to")
    friends_from = relationship("FriendRequests", foreign_keys="FriendRequests.user_id_from")
    friends_1 = relationship("FriendShip", foreign_keys="FriendShip.user_id_1")
    my_friends = relationship("FriendShip", foreign_keys="FriendShip.user_id_2")
    user_items_owner = relationship("Item", foreign_keys="Item.owner_id")
    user_items_giver = relationship("Item", foreign_keys="Item.giver_id")


class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    about = Column(String(1000))
    access_level = Column(AccessLevelEnum, nullable=False)


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    about = Column(String(1000))
    access_level = Column(AccessLevelEnum, nullable=False)
    status = Column(StatusEnum, nullable=False)
    giver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date_creation = Column(DateTime(), nullable=False)
    list_id = Column(Integer, ForeignKey('wishlist.id'))
    date_for_status = Column(DateTime(), nullable=False)
    degree = Column(DegreeEnum)
    giver = relationship("User", foreign_keys=[giver_id])
    owner = relationship("User", foreign_keys=[owner_id])


class ItemPicture(Base):
    __tablename__ = "item_picture"
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    path_to_picture = Column(Text(), primary_key=True)


class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    about = Column(String(1000))
    access_level = Column(AccessLevelEnum, nullable=False)
    date_creation = Column(DateTime(), nullable=False)
    date = Column(DateTime(), nullable=False)
'''
    def from_dict(self, data, new_user=False):
        for field in ['username', 'nickname', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])
            self.last_seen = datetime.now().isoformat() + 'Z'
'''

class GroupList(Base):
    __tablename__ = "group_list"
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    wishlist_id = Column(Integer, ForeignKey('wishlist.id'), primary_key=True)


class ItemGroup(Base):
    __tablename__ = "item_group"
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)


class GroupUser(Base):
    __tablename__ = "group_user"
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_in_group = Column(RoleEnum, nullable=False)


Base.metadata.create_all(engine)
