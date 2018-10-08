# encoding: utf-8

from wtforms import Form


class BaseForm(Form):
    def get_error(self):
        s = []
        for i in self.errors.values():
            for j in i:
                s += [j]
        message = s
        return message

    def validate(self):
        return super(BaseForm, self).validate()
