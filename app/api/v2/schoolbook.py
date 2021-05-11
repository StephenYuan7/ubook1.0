from flask import current_app, jsonify

from app.libs.red_print import Redprint
from app.libs.token_auth import auth
from app.models.school import School
from app.models.schoolbook import Schoolbook
from app.validators.forms import SchoolbookForm

api = Redprint('schoolbook')


@api.route('/look', methods=['POST'])
@auth.login_required
def look_schoolbook():
    form = SchoolbookForm().validate_for_api()
    page = current_app.config['PAGE']
    schoolbooks = Schoolbook.query.filter_by(school_id=form.school_id.data,grade=form.grade.data
                                             , academy=form.academy.data,term=form.term.data).all()
    schoolbooks = schoolbooks[form.page.data*page-page:form.page.data*page]
    name = []
    for schoolbook in schoolbooks:
        name.append(schoolbook.name)
    return jsonify(name)
