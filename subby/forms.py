'Forms for flaskbb-plugin-subby'

# 3rd party
from flask_babelplus import gettext as _
from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, SubmitField
from wtforms.validators import Optional
# local
from .wtforms_extended_selectfield import ExtendedSelectField


class SubsManageForm(FlaskForm):

    'Subscription settings form'

    tracked_topics = BooleanField(_('Include tracked topics'))
    email = BooleanField(_('Send email notifications'))
    forums = ExtendedSelectField(_('Forums'), [Optional()], coerce=int)
    submit = SubmitField(_('Submit'))
