from sqlalchemy import Column, Integer, String, ForeignKey

from app.models.base import Base, db


class Activity(Base):
    id = Column(Integer, primary_key=True, nullable=False)
    organizer = Column(String(100))
    activity_time = Column(Integer)
    over_time = Column(Integer)
    description = Column(String(5000))
    title = Column(String(100))
    image  = Column(String(100))
    icon  = Column(String(100))
    school_id = Column(Integer, ForeignKey("school.id"),nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __init__(self):
        if self.create_time is None:
            super(Activity, self).__init__()

    def keys(self):
        return ['id', 'organizer', 'activity_time', 'over_time',
                'description', 'title', 'image', 'icon', 'school_id'
                ,'user_id']

    @staticmethod
    def up_by_mina(organizer, activity_time, over_time, description, title, school_id, user_id):
        with db.auto_commit():
            activity = Activity()
            activity.organizer = organizer
            activity.activity_time = activity_time
            activity.title = title
            activity.over_time = over_time
            activity.description = description
            activity.school_id = school_id
            activity.user_id = user_id

            db.session.add(activity)
        return {"activity_id":activity.id}