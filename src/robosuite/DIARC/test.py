import re


def decomposeAction(action):
    split_symbols = '(:,)'
    start_letters = ["peg", "cub"]
    split_pattern = f"[{re.escape(split_symbols)}]"
    components = re.split(split_pattern, action)
    base_action = components[0]
    objects = [word for word in components if word[:3] in start_letters]
    print(objects)
    if base_action == "reach_pick":
        toMove = objects[1]
        destination = objects[0]
    elif base_action == "pick":
        toMove = objects[0]
        destination = objects[1]
    elif base_action == "reach_drop":
        toMove = objects[0]
        destination = objects[2]
    else:
        toMove = objects[0]
        destination = objects[1]
    return base_action, toMove, destination



plan_action = "drop(cube1:disc,peg3:stackable)"
# plan_action = "reach_drop(cube1:disc,peg3:stackable,cube2:disc)"
base_action, toMove, destination = decomposeAction(plan_action)
print(base_action, toMove, destination)


