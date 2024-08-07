import robosuite as suite
from robosuite.DIARC.detector import Detector
import numpy as np
from robosuite import load_controller_config
import time
import re
"""
Functions specific to domain for tower of hanoi problem in robosuite
"""

controller_config = load_controller_config(default_controller='OSC_POSITION')

#Executor mapping
executors = {
     'pick': '../operators/pick_sac.zip',
     'drop': '../operators/drop_ppo.zip',
     'reach_drop': '../operators/reachdrop_sac.zip',
     'reach_pick': '../operators/reach_pick_sac.zip'
}

obj_mapping = {}
area_pos = {}

#Effects for post condition check to make sure operator successful
effect_mapping = {
     'reach_pick': [True],
     'pick': [True],
     'reach_drop': [True, True],
     'drop': [True, False]
}

#Expected effects of each operator
def effects(operator, symgoal):
     if operator == 'reach_pick':
          return [f'over(gripper,{symgoal})']
     elif operator == 'pick':
          return [f'grasped({symgoal})']
     elif operator == 'reach_drop':
          return [f'over(gripper,{symgoal[1]})',f'grasped({symgoal[0]})']
     else:
          print(f"on({symgoal[0]},{symgoal[1]})")
          time.sleep(5)
          return [f'on({symgoal[0]},{symgoal[1]})',f'grasped({symgoal[0]})']
     

#Object mapping to robosuite environment
def populateExecutorInfo(env):
     #Domain synapses here on down
        cube1_body = env.sim.model.body_name2id('cube1_main')
        cube2_body = env.sim.model.body_name2id('cube2_main')
        cube3_body = env.sim.model.body_name2id('cube3_main')
        peg1_body = env.sim.model.body_name2id('peg1_main')
        peg2_body = env.sim.model.body_name2id('peg2_main')
        peg3_body = env.sim.model.body_name2id('peg3_main')

        global obj_mapping
        global area_pos

        obj_mapping = {'cube1': cube1_body, 
                            'cube2': cube2_body, 
                            'cube3': cube3_body, 
                            'peg1': peg1_body, 
                            'peg2': peg2_body, 
                            'peg3': peg3_body}
        

        area_pos = {'peg1': env.pegs_xy_center[0], 'peg2': env.pegs_xy_center[1], 'peg3': env.pegs_xy_center[2]}




#Create robosuite tower of hanoi environment
def create_env(env_id, rand_rest = False):
    print(f"Creating env ID: {env_id}, random reset {rand_rest}")


    if env_id == "standard":
        # create environment instance
        env = suite.make(
            env_name="Hanoi",
            robots="Kinova3", 
            has_renderer=True,
            has_offscreen_renderer=False,
            use_camera_obs=False,
            # render_camera="agentview",
            controller_configs=controller_config,
            random_reset = rand_rest,
            ignore_done=True if not rand_rest else False

        )
    else:
        env = suite.make(
            env_name="DoorNovelty",
            robots="Kinova3", 
            has_renderer=True,
            has_offscreen_renderer=False,
            use_camera_obs=False,
            # render_camera="agentview",
            controller_configs=controller_config,
            random_reset = rand_rest,
            ignore_done=True if not rand_rest else False
        )

    return env

#Append goal to observation space, mapping symbolic goal back to sub-symbolic data representation
def addGoal(obs, symgoal, env, operator):
    if operator in ["reach_pick", "pick"]:
        obs = np.concatenate((obs, env.sim.data.body_xpos[obj_mapping[symgoal]][:3]))
    else:
        obs = np.concatenate((obs, env.sim.data.body_xpos[obj_mapping[symgoal[1]]][:3]))
    return obs

#Symbolic termination for beta
def termination_indicator(operator):

    if operator == 'pick':

        def Beta(env, symgoal):

            detector = Detector(env)

            state = detector.get_groundings(as_dict=True, binary_to_float=False, return_distance=False)

            condition = state[f"grasped({symgoal})"]

            return condition

    elif operator == 'drop':

        def Beta(env, symgoal):

            detector = Detector(env)

            state = detector.get_groundings(as_dict=True, binary_to_float=False, return_distance=False)

            condition = state[f"on({symgoal[0]},{symgoal[1]})"] and not state[f'grasped({symgoal[0]})']

            return condition

    elif operator == 'reach_pick':

        def Beta(env, symgoal):

            detector = Detector(env)

            state = detector.get_groundings(as_dict=True, binary_to_float=False, return_distance=False)

            condition = state[f"over(gripper,{symgoal})"]

            return condition

    elif operator == 'reach_drop':

        def Beta(env, symgoal):

            detector = Detector(env)

            state = detector.get_groundings(as_dict=True, binary_to_float=False, return_distance=False)

            condition = state[f"over(gripper,{symgoal[1]})"] and state[f'grasped({symgoal[0]})']
            return condition

    return Beta



#Decompose the action passed in by DIARC into operator and symbolic goals
def decomposeAction(action):
    action = str(action)
    split_symbols = '(:,)'
    start_letters = ["peg", "cub"]
    try:
        split_pattern = f"[{re.escape(split_symbols)}]"
        components = re.split(split_pattern, action)
    except Exception as e: 
        print(e)
    
    base_action = components[0]
    objects = [word for word in components if word[:3] in start_letters]
    # print(objects)
    if base_action == "reach_pick":
        toMove = objects[1]
        destination = objects[0]
        symgoal = toMove
    elif base_action == "pick":
        toMove = objects[0]
        destination = objects[1]
        symgoal = toMove
    elif base_action == "reach_drop":
        toMove = objects[0]
        destination = objects[2]
        symgoal = [toMove, destination]
    else:
        toMove = objects[0]
        destination = objects[1]
        symgoal = [toMove, destination]
    return base_action, symgoal