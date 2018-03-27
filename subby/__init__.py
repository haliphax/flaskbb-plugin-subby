'Entry point for flaskbb-plugin-subby'

# stdlib
from logging import getLogger
from os.path import dirname, join
# 3rd party
from flask import request
from flask_babelplus import gettext as _
from flask_login import current_user
from flaskbb.email import send_async_email
from flaskbb.forum.models import Category, Topic, topictracker
from flaskbb.user.models import User
from flaskbb.utils.helpers import real
from flaskbb.utils.markup import markdown
from sqlalchemy import text
# local
from .models import Subscription, SubscriptionSettings
from .views import blueprint

log = getLogger(__name__)


def flaskbb_load_migrations():
    return join(dirname(__file__), 'migrations')


def flaskbb_tpl_profile_settings_menu():
    'Profile settings menu template hook'

    return [
        ('plugins.subby.manage', _('Subscription Settings')),
    ]


def flaskbb_load_blueprints(app):
    'Blueprints hook'

    app.register_blueprint(blueprint, url_prefix='/subscription')


def flaskbb_event_post_save_after(post, is_new):
    'After-post hook'

    if not is_new:
        return

    url_root = (request.url_root[:-1] if request.url_root[-1] == '/'
                else request.url_root)
    subs = (Subscription.query.filter(
        Subscription.forum_id == post.topic.forum_id)
        .join(User)
        .filter(User.id != current_user.id)
        .join(SubscriptionSettings)
        .filter(SubscriptionSettings.email)
        .all())
    tracked = (User.query.filter(User.id != current_user.id)
        .join(SubscriptionSettings)
        .filter(SubscriptionSettings.tracked_topics
            & SubscriptionSettings.email)
        .join(topictracker)
        .filter(text('topictracker.topic_id==' + str(post.topic_id)))
        .all())
    users = set([sub.user for sub in subs] + tracked)
    content = markdown.render(post.content)
    html_body = (u'{url}\n\n{author_label}: {author}\n\n{content}'
                 .format(url=url_root + post.url, author_label=_(u'Author'),
                         author=post.user.username, content=content))
    text_body = _(u'HTML message')
    subject = _(u'New post in {forum}: {title}').format(
        forum=post.topic.forum.title, title=post.topic.title)

    for user in users:
        categories = Category.get_all(user=real(user))
        allowed_forums = []

        for category, forums in categories:
            for forum, forumsread in forums:
                allowed_forums.append(forum.id)

        if post.topic.forum_id not in allowed_forums:
            log.warn(u'{user} is not allowed in forum {forum} (#{id})'
                     .format(user=user.username, forum=post.topic.forum.title,
                             id=post.topic.forum_id))
            continue

        send_async_email(subject=subject, recipients=[user.email],
                         text_body=text_body, html_body=html_body)
