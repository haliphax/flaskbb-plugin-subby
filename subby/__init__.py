'Entry point for flaskbb-plugin-subby'

# stdlib
from os.path import dirname, join
# 3rd party
from flask import request
from flask_babelplus import gettext as _
from flaskbb.email import send_async_email
from flaskbb.forum.models import Topic, topictracker
from flaskbb.user.models import User
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
        .join(SubscriptionSettings)
        .filter(SubscriptionSettings.email)
        .all())
    tracked = (User.query.join(SubscriptionSettings).filter(
        SubscriptionSettings.tracked_topics)
        .filter(SubscriptionSettings.email)
        .join(topictracker)
        .filter(text('topictracker.topic_id==' + str(post.topic_id)))
        .all())
    emails = set([sub.user.email for sub in subs]
                 + [user.email for user in tracked])
    content = markdown.render(post.content)
    html_body = '{url}\n\n{content}'.format(url=url_root + post.url,
                                            content=content)
    text_body = _('HTML message')
    subject = _('New post in {forum}: {title} (by {author})').format(
        forum=post.topic.forum.title, title=post.topic.title,
        author=post.user.username)

    for email in emails:
        send_async_email(subject=subject, recipients=[email],
                         text_body=text_body, html_body=html_body)
