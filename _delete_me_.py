import template_new
from template_new.syntax.telegram import TELEGRAM

render = template_new.render('apps/debug/templates/new_templater_test.xml', {}, syntax=TELEGRAM).extract()
print(render.text)
