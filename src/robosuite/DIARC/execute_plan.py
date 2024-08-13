from planner import *
from robosuite.DIARC.executor_noHRL import Executor
from robosuite.DIARC.domain_synapses import *
from robosuite.wrappers.gym_wrapper import GymWrapper
import time
from learner import Learner


"""
This file is to execute the plan outside of DIARC, used for testing operators
in robosuite and generic parsing
"""

#Decompose action in PDDL plan
def decomposeAction(action):
    print("Decomposing")
    action = action.lower()
    components = action.split(' ')
    base_action = components[0]
    if base_action == "reach_pick":
        toMove = components[2]
    else:
        toMove = components[1]
    if base_action == "reach_drop":
        destination = components[3]
    else:
        destination = components[2]
    return base_action, toMove, destination
    
    
#Execute proper executor from action
def executeAction(base_action, toMove, destination, env):
    print(base_action, toMove, destination)


    if base_action == "reach_pick":
        executor = Executor(env, 'reach_pick')
        success = executor.execute_policy(symgoal=toMove, render=True)
        if not success:
            print("Reach pick failed")
            return False
        return True
    
    
    elif base_action == "pick":
        executor = Executor(env, 'pick')
        success = executor.execute_policy(symgoal=toMove, render=True)
        if not success:
            print("Pick failed")
            return False
        return True
    
    elif base_action == "reach_drop":
        executor = Executor(env, 'reach_drop')
        success = executor.execute_policy(symgoal=[toMove,destination], render=True)
        if not success:
            print("Reach drop failed")
            return False
        return True
    
    else:
        executor = Executor(env, 'drop')
        success = executor.execute_policy(symgoal=[toMove,destination], render=True)
        if not success:
            print("Drop failed")
            return False
        
        return True

#Learner for failed operator
def call_learner(operator, env):
    print(f"Learning new operator {operator}")
    learner = Learner(env, operator)
    learner.learn()
    print("New operator learned")
    


if __name__ == "__main__":
    pddl_dir = "../PDDL"
    domain_dir = "Domains"
    problem_dir = "Problems"
    domain = "domain"
    problem = "problem"

    domain_path = pddl_dir + os.sep + domain + ".pddl"
    problem_path = pddl_dir + os.sep + problem + ".pddl"
    print("Solving tower of Hanoi task")
        
    plan, game_action_set = call_planner(domain_path, problem_path)
    print(plan)
    plan = ['REACH_PICK PEG2 CUBE1', 'PICK CUBE1 CUBE2', 'REACH_DROP CUBE1 CUBE2 PEG1', 'DROP CUBE1 PEG1']

    # #Solve task on standard env - will complete
    # env = create_env("standard", rand_rest=False)
    # env = GymWrapper(env, keys=['robot0_proprio-state', 'object-state'])


    # for action in plan:
    #     base_action, toMove, destination = decomposeAction(action)
    #     success = executeAction(base_action, toMove, destination, env)
    #     if not success:
    #         print("Task failed...")
    #         task_learned = call_learner(base_action, env)
    #         break

    #Solve task on door novelty, should fail and learn
    env = create_env("door", rand_rest=False)
    env = GymWrapper(env, keys=['robot0_proprio-state', 'object-state'])
    for action in plan:
        base_action, toMove, destination = decomposeAction(action)
        success = executeAction(base_action, toMove, destination, env)
        if not success:
            print("Task failed...")
            task_learned = call_learner(base_action, env)
            break

    