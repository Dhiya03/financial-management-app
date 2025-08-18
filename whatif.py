from persistence import get_scenarios, update_data
from transactions import add_transaction

def add_scenario(name, changes):
    scenarios = get_scenarios()
    scenarios[name] = changes  # changes: list of dict {category, amount, start, end}
    update_data("scenarios", scenarios)

def apply_scenario(year, month, name):
    scenarios = get_scenarios()
    if name not in scenarios:
        return
    for change in scenarios[name]:
        start_year, start_month = map(int, change["start"].split("-"))
        end_year, end_month = map(int, change["end"].split("-"))
        if (year > end_year or year < start_year) or (year == start_year and month < start_month) or (year == end_year and month > end_month):
            continue
        add_transaction(year, month, change["category"], change["amount"], description=f"Scenario: {name}")
