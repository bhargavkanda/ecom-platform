from celery import task
from .models import Trigger
from .utils import get_model_from_name
import pdb

def equal(left_val, right_val):
    if left_val == right_val:
        return True
    return False
def contains(left_val, right_val):
    if right_val in left_val:
        return True
    return False
def gt(left_val, right_val):
    if left_val > right_val:
        return True
    return False
def gte(left_val, right_val):
    if left_val >= right_val:
        return True
    return False
def lt(left_val, right_val):
    if left_val < right_val:
        return True
    return False
def lte(left_val, right_val):
    if left_val <= right_val:
        return True
    return False
def startswith(left_val, right_val):
    if left_val.startswith(right_val):
        return True
    return False
def endswith(left_val, right_val):
    if left_val.endswith(right_val):
        return True
    return False
def left_in_right(left_val, right_val):
    if left_val in right_val:
        return True
    return False


def check_rules(rules, data):
    # presave_data = data['presave_data']
    # pdb.set_trace()
    conditional_dict = { 'equal':equal, 'contains':contains, 'gt':gt, 'gte':gte, 'lt':lt, 'lte':lte, 
        'startswith':startswith, 'endswith':endswith, 'in': left_in_right
        }


    for rule in rules:
        left_val = data.get(rule.left_save_method).get(rule.left_field_name)
        right_val = rule.right_static or data.get(rule.right_save_method).get(rule.right_field_name)
        if not conditional_dict.get(rule.lookup_type)(left_val, right_val):
            return False
    return True




@task
def signal_triggers(signal_context):
    # pdb.set_trace()
    triggers = Trigger.objects.filter(
        model=signal_context.get('model'), option=signal_context.get('option'))
    selected_model = get_model_from_name(signal_context.get(
                'model'))
    model_obj = selected_model.objects.get(id=signal_context.get(
                'model_id'))

    for trigger in triggers:
        rules = trigger.rules.all()
        if check_rules(rules, {'presave':signal_context.get('presave_data'), 'postsave':model_obj.__dict__}):
            for drip in trigger.trigger_drip.all():
                drip_base = drip.drip_with_context(context={signal_context.get(
                    'model'): signal_context.get('model_id'), 'ZapUser': signal_context.get('user_id')})
                drip_base.send()
