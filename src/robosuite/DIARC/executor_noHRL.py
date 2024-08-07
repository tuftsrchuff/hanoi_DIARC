
'''
# This files implements the structure of the executor object used to execute the hierarchical policies
'''
from stable_baselines3 import SAC, PPO
from robosuite.DIARC.detector import Detector
from robosuite.DIARC.domain_synapses import *
import numpy as np
import time
import os


class Executor():
    def __init__(self, env, operator):
        self.env = env
        self.detector = Detector(env)

        #Must cast Java string object to python string in DIARC
        self.operator = str(operator)

        populateExecutorInfo(env)

    
    def execute_policy(self,
                       symgoal = None, render=False): 
        print("Starting policy execution")
        print(f"Executor path {executors[self.operator]}")


        done = False
        rew_eps = 0
        step_executor = 0
        try:
            if self.operator in ["drop"]:
                model = PPO.load(executors[self.operator])
            else:
                model = SAC.load(executors[self.operator])

            #Base action to return observation
            base_action = np.zeros(len(self.env.action_space.sample()))
            obs, _, _, _, _ = self.env.step(base_action)

            #addGoal to obs space for agent execution
            obs = addGoal(obs, symgoal, self.env, self.operator)

            #Indication for whether goal met
            Beta = termination_indicator(self.operator)
            terminated = False
            print(symgoal)


            #Pass in initial observation   
            while not done and not terminated:
                action, _states = model.predict(obs)
                obs, reward, terminated, truncated, info = self.env.step(action)

                #addGoal
                obs = addGoal(obs, symgoal, self.env, self.operator)
                step_executor += 1
                rew_eps += reward
                done = Beta(self.env, symgoal)

                #Render issue with OpenGL inside JVM
                if render:
                    self.env.render()


                if step_executor > 1000:
                    done = True


            # comparing execution effects to expected effects
            new_state = self.detector.get_groundings(self.env)


            expected_effects_keys = effects(self.operator, symgoal)

            #Compare looks at all predicates in new state and checks if it exists in grounded
            #predicates in old state, if not adds it to the execution_effects
            execution_effects = []
            for effect in expected_effects_keys:
                execution_effects.append(new_state[effect])

            expected_effects = effect_mapping[self.operator]
            print(f"Expected effects {expected_effects}")
            print(f"Execution efects {execution_effects}")

            success = True
            del model
            for i, val in enumerate(execution_effects):
                if expected_effects[i] != val:
                    success = False
                    break
            if success:
                return True
            else:
                print(f"{self.operator} failed...")
                return False
        except Exception as e:
            print(e)
            del model
