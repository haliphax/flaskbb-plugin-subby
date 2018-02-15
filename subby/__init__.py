'Entry point for flaskbb-plugin-subby'

# stdlib
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


def flaskbb_evt_after_post(post, is_new):
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
    html_body = '{url}\n\n{content}'.format(url=url_root + post.url,
                                            content=content)
    text_body = _('HTML message')
    subject = _('New post in {forum}: {title} (by {author})').format(
        forum=post.topic.forum.title, title=post.topic.title,
        author=post.user.username)

    for user in users:
        categories = Category.get_all(user=real(user))
        allowed_forums = [r[0].id for r in [r for x, r in categories][0]]

        if post.topic.forum_id not in allowed_forums:
            continue

        send_async_email(subject=subject, recipients=[user.email],
                         text_body=text_body, html_body=html_body)
