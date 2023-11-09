
from chat.models import BroadcastPlan


def calculate_cost(selected_plan_id):
    try:
        selected_plan = BroadcastPlan.objects.get(pk=selected_plan_id)
    except BroadcastPlan.DoesNotExist:
        return 0  # Return a default cost or handle the error as needed

    # Calculate the cost based on the selected plan's price
    return selected_plan.price
