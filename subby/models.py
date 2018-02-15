'Models for flaskbb-plugin-subby'

# stdlib
from uuid import uuid4
# 3rd party
from flaskbb.extensions import db
from flaskbb.utils.database import CRUDMixin


class SubscriptionSettings(db.Model, CRUDMixin):

    'Subscription settings for user'

    __tablename__ = 'subby_settings'

    #: ID of the user
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'),
                        primary_key=True, nullable=False)
    #: Include tracked topics
    tracked_topics = db.Column(db.Boolean, nullable=False, default=False)
    #: Enable email notifications
    email = db.Column(db.Boolean, nullable=False, default=True)
    #: RSS key
    rss_key = db.Column(db.String)
    #: Settings owner
    user = db.relationship('User', lazy='joined', foreign_keys=(user_id,))

    def save(self):
        'Saves subscription settings'

        if not self.rss_key:
            self.rss_key = SubscriptionSettings._regenerate_rss_key()

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def _regenerate_rss_key():
        'Regenerates unique RSS key'

        return str(uuid4())


class Subscription(db.Model, CRUDMixin):

    'Forum subscriptions for user'

    __tablename__ = 'subby_subscriptions'

    #: ID of the user
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'),
                        primary_key=True, nullable=False)
    #: ID of a forum they subscribe to
    forum_id = db.Column(db.Integer,
                         db.ForeignKey('forums.id', ondelete='CASCADE'),
                         primary_key=True, nullable=False)
    #: Subscription owner
    user = db.relationship('User', lazy='joined', foreign_keys=(user_id,))
    #: Forum subscribed to
    forum = db.relationship('Forum', lazy='joined', foreign_keys=(forum_id,))

    def save(self):
        'Saves forum subscription'

        db.session.add(self)
        db.session.commit()

        return self
