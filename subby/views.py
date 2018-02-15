'Views for flaskbb-plugin-subby'

# 3rd party
from flask import Blueprint, redirect, request, url_for, flash
from flask.views import MethodView
from flask_babelplus import gettext as _
from flask_login import current_user
from flaskbb.extensions import db
from flaskbb.forum.models import Category, Post, Topic
from flaskbb.utils.helpers import real, render_template, register_view
from flaskbb.utils.markup import markdown
from werkzeug.contrib.atom import AtomFeed
# local
from .forms import SubsManageForm
from .models import Subscription, SubscriptionSettings

blueprint = Blueprint('plugins.subby', __name__, template_folder='templates')


class SubsManage(MethodView):

    'Subscription settings view'

    def get(self):
        'Handle GET request'

        subs = [r.forum_id for r in
                Subscription.query.filter(
                    Subscription.user_id==current_user.id)
                .all()]
        settings = SubscriptionSettings.query.filter(
            SubscriptionSettings.user_id==current_user.id).first()

        if not settings:
            settings = SubscriptionSettings(user_id=current_user.id)

        form = SubsManageForm(obj=settings)
        form.forums.choices = self._get_choices()
        form.forums.data = subs

        return render_template('manage.html', form=form)

    def post(self):
        'Handle POST request'

        settings = SubscriptionSettings.query.filter(
            SubscriptionSettings.user_id==current_user.id).first()

        if not settings:
            settings = SubscriptionSettings(user_id=current_user.id)

        form = SubsManageForm(request.form, obj=settings)
        form.forums.choices = self._get_choices()

        if form.validate():
            Subscription.query.filter(
                Subscription.user_id == current_user.id).delete()
            db.session.commit()
            forums = [form.forums.data]

            if type(form.forums.data) in (list, tuple):
                forums = form.forums.data
            elif form.forums.data is None:
                forums = []

            for forum_id in forums:
                (Subscription(user_id=current_user.id, forum_id=forum_id)
                    .save())

            form.populate_obj(settings)
            settings.save()
        else:
            flash(_('Error updating subscription settings'))

        return redirect(url_for('plugins.subby.manage'))

    def _get_choices(self):
        'Get list of forums to choose from'

        return [
            (category.title, [(forum.id, forum.title) for forum, x in forums])
            for category, forums in Category.get_all(user=real(current_user))
        ]


register_view(blueprint, routes=['/manage'],
              view_func=SubsManage.as_view('manage'))


@blueprint.route('/rss')
def rss_tmp():
    'Temporary filler'

    return rss(0)


@blueprint.route('/rss/<key>')
def rss(key):
    'Personalized RSS feed'

    # @TODO get user.id and settings from DB for given key
    forums = (1,)
    url_root = (request.url_root[:-1] if request.url_root[-1] == '/'
                else request.url_root)
    feed = AtomFeed(_('Recent posts'), feed_url=request.url, url=url_root)
    posts = (Post.query.filter(Post.user_id != 1)
             .join(Topic, Post.topic)
             .filter(Topic.forum_id.in_(forums))
             .order_by(Post.date_created.desc())
             .limit(10)
             .all())

    for post in posts:
        feed.add(_('{title} by {user}').format(title=post.topic.title,
                                               user=post.username),
                 markdown.render(post.content), content_type='html',
                 author=post.username, url=url_root + post.url,
                 updated=post.date_modified or post.date_created,
                 published=post.date_created)

    return feed.get_response()
