import numpy as np
import robosuite as suite
from robosuite.wrappers.behavior_cloning.hanoi_reach_pick import ReachPickWrapper
from robosuite.wrappers.behavior_cloning.hanoi_reach_drop import ReachDropWrapper
from robosuite.wrappers.behavior_cloning.hanoi_pick import PickWrapper
from robosuite.wrappers.behavior_cloning.hanoi_drop import DropWrapper
import os
from robosuite.wrappers.gym_wrapper import GymWrapper
from stable_baselines3 import SAC, PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from robosuite import load_controller_config
from robosuite.DIARC.detector import Detector
from robosuite.DIARC.domain_synapses import *
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback, CallbackList, StopTrainingOnNoModelImprovement
import time
from robosuite.DIARC.executor_noHRL import Executor

controller_config = load_controller_config(default_controller='OSC_POSITION')
TRAINING_STEPS = 1000000


class Learner():
    def __init__(self, env, operator):
        print("Creating learner init class")
        self.env = env
        self.detector = Detector(env)
        self.operator = operator

        populateExecutorInfo(env)

        self.env = create_env("standard", rand_rest=True)

        self.eval_env = create_env("standard", rand_rest=True)

        self.env = GymWrapper(self.env, keys=['robot0_proprio-state', 'object-state'])
        self.eval_env = GymWrapper(self.eval_env, keys=['robot0_proprio-state', 'object-state'])

        #Wrap environment in proper wrapper
        if self.operator == 'reach_pick':
            self.env = ReachPickWrapper(self.env)
            self.eval_env = ReachPickWrapper(self.eval_env)
        elif self.operator == 'pick':
            self.env = PickWrapper(self.env)
            self.eval_env = PickWrapper(self.eval_env)
        elif self.operator == 'reach_drop':
            self.env = ReachDropWrapper(self.env)
            self.eval_env = ReachDropWrapper(self.eval_env)
        else:
            self.env = DropWrapper(self.env)
            self.eval_env = DropWrapper(self.eval_env)

    def eval_policy(self):
        #Create new env, wrap and run for 10 runs
        self.env.reset()
        self.eval_env.reset()

        executor = Executor(self.env, 'reach_pick')
        success = executor.execute_policy(symgoal="cube1")


        #Must be successful more than 90% of time to return tr
        return True
    

    def loadAndEval(self):
        #Do max 10 evals, if any eval of 10 trials fails then retrain
        #Otherwise return True, policy good to go - after 10 evals return False
        pass

    
    def learn(self):
        print(f"Learning {self.operator}")
        #Call train 
        self.env = Monitor(self.env, filename=None, allow_early_resets=True)

        if self.operator == "drop":
            model = PPO("MlpPolicy", self.env, verbose=1)

        else:
            model = SAC(
            'MlpPolicy',
            self.env,
            learning_rate=0.0003,
            buffer_size=int(1e6),
            learning_starts=10000,
            batch_size=256,
            tau=0.005,
            gamma=0.99,
            policy_kwargs=dict(net_arch=[256, 256]),
            verbose=1,
            tensorboard_log='./logs/'
            )

        self.eval_env = Monitor(self.eval_env, filename=None, allow_early_resets=True)



        # Define the evaluation callback
        eval_callback = EvalCallback(
        self.eval_env,
        best_model_save_path=f'./models/{self.operator}',
        log_path='./logs/',
        eval_freq=10000,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        callback_on_new_best=None,
        verbose=1
        )

        # Train the model
        model.learn(
            total_timesteps=TRAINING_STEPS,
            callback=eval_callback,
            progress_bar=True
        )

        # Save the model
        model.save(os.path.join(f'../operators/{self.operator}_postfail'))
        if self.operator != "drop":
            model.save_replay_buffer(f'../operators/{self.operator}_postfail_buffer')

        executors[self.operator] = f'../operators/{self.operator}_postfail.zip'
        print(f"Executor file location {executors[self.operator]}")

        #Policy evaluation for 10 evals needs to reach goal, otherwise train more
        # for i in range(10):
        #     result = self.eval_policy()
        #     if result == False: return False

        return True

