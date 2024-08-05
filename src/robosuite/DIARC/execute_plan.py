from planner import *
from robosuite.DIARC.executor_noHRL import Executor
from robosuite.DIARC.domain_synapses import *
from robosuite.wrappers.gym_wrapper import GymWrapper
import time
from learner import Learner

def decomposeAction(action):
    print("Decomposing")
    action = action.lower()
    components = action.split(' ')
    base_action = components[0]
    toMove = components[1]
    destination = components[3]
    return base_action, toMove, destination
    
    

def executeAction(base_action, toMove, destination, env):

    print(f"Taking action {base_action}")
    #Post condition can be looked at here - toMove should be on destination
    print(f"Reach-pick {toMove} to {destination}")
    # obs = np.concatenate((obs, self.env.sim.data.body_xpos[self.obj_mapping[self.obj_to_pick]][:3]))
    
    executor = Executor(env, 'reach_pick')
    success = executor.execute_policy(symgoal=toMove)
    if not success:
        print("Reach pick failed")
        return False
    # time.sleep(5)

    #Terminated environment, use base env and rewrap?
    print(f"Pick {toMove}")
    # exec_env = GymWrapper(env, keys=['robot0_proprio-state', 'object-state'])
    executor = Executor(env, 'pick')
    success = executor.execute_policy(symgoal=toMove)
    if not success:
        print("Pick failed")
        return False
    # time.sleep(5)

    print(f"Reach-drop {destination}")
    # exec_env = GymWrapper(env, keys=['robot0_proprio-state', 'object-state'])
    executor = Executor(env, 'reach_drop')
    success = executor.execute_policy(symgoal=[toMove,destination])
    if not success:
        print("Reach drop failed")
        return False
    # time.sleep(5)

    print(f"Dropping {destination}")
    # exec_env = GymWrapper(env, keys=['robot0_proprio-state', 'object-state'])
    executor = Executor(env, 'drop')
    success = executor.execute_policy(symgoal=[toMove,destination])
    if not success:
        print("Drop failed")
        return False
    else:
        print(f"Action {base_action} {toMove} onto {destination} finished successfully")
        return True


def call_learner(operator, env):
    print(f"Learning new operator {operator}")
    learner = Learner(env, operator)
    learner.learn()
    print("New operator learned")
    time.sleep(5)


if __name__ == "__main__":
    pddl_dir = "../PDDL"
    domain_dir = "Domains"
    problem_dir = "Problems"
    domain = "domain"
    problem = "problem"

    domain_path = pddl_dir + os.sep + domain + ".pddl"
    problem_path = pddl_dir + os.sep + problem + ".pddl"
    print("Solving tower of Hanoi task")
    env = create_env("ReachPick")
    env = GymWrapper(env, keys=['robot0_proprio-state', 'object-state'])

    
    plan, game_action_set = call_planner(domain_path, problem_path)
    print(plan)
    for action in plan:
        base_action, toMove, destination = decomposeAction(action)
        success = executeAction(base_action, toMove, destination, env)
        if not success:
            print("Plan failed")
            break