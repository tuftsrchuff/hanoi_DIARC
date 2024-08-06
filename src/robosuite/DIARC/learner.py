import numpy as np
import robosuite as suite
from robosuite.wrappers.behavior_cloning.hanoi_reach_pick import ReachPickWrapper
from robosuite.wrappers.behavior_cloning.hanoi_reach_drop import ReachDropWrapper
from robosuite.wrappers.behavior_cloning.hanoi_pick import PickWrapper
from robosuite.wrappers.behavior_cloning.hanoi_drop import DropWrapper
import os
from robosuite.wrappers.gym_wrapper import GymWrapper
from stable_baselines3 import SAC
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
from robosuite import load_controller_config
from robosuite.DIARC.detector import Detector
from robosuite.DIARC.domain_synapses import *
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback, CallbackList, StopTrainingOnNoModelImprovement
import time

controller_config = load_controller_config(default_controller='OSC_POSITION')
TRAINING_STEPS = 1000000


class Learner():
    def __init__(self, env, operator):
        self.env = env
        self.detector = Detector(env)
        self.operator = operator

        populateExecutorInfo(env)

        self.env = create_env("door", rand_rest=True)

        self.eval_env = create_env("door", rand_rest=True)

        self.env = GymWrapper(self.env, keys=['robot0_proprio-state', 'object-state'])
        self.eval_env = GymWrapper(self.eval_env, keys=['robot0_proprio-state', 'object-state'])

        #Wrap environment in proper wrapper
        if self.operator == 'reach_pick':
            self.env = ReachPickWrapper(self.env)
        elif self.operator == 'pick':
            self.env = PickWrapper(self.env)
        elif self.operator == 'reach_drop':
            self.env = ReachDropWrapper(self.env)
        else:
            self.env = DropWrapper(self.env)

    def success_rate(self):
        #Create new env, wrap and run for 10 runs

        #Must be successful more than 90% of time to return tr
        pass

    
    def learn(self):
        print(f"Learning {self.operator}")
        time.sleep(5)
        #Call train 
        self.env = Monitor(self.env, filename=None, allow_early_resets=True)


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
            tensorboard_log=f"./sac_novelty_{self.operator}_tensorboard/"
        )

        self.eval_env = Monitor(self.eval_env, filename=None, allow_early_resets=True)

        callbacks = []

        stop_train_callback = StopTrainingOnNoModelImprovement(max_no_improvement_evals=100000, min_evals=300000, verbose=1)



        # Define the evaluation callback
        eval_callback = EvalCallback(
            self.eval_env,
            best_model_save_path=f'./models/{self.operator}_failed',
            log_path='./logs/',
            eval_freq=10000,
            n_eval_episodes=10,
            deterministic=True,
            render=False,
            callback_on_new_best=None,
            verbose=1,
            callback_after_eval=stop_train_callback
        )

        callbacks.append(eval_callback)


        callbacks.append(stop_train_callback)

        # Train the model
        model.learn(
            total_timesteps=TRAINING_STEPS,
            callback=CallbackList(callbacks),
            progress_bar=True
        )

        # Save the model
        model.save(os.path.join(f'../operators/{self.operator}_postfail'))
        model.save_replay_buffer(f'../operators/{self.operator}_postfail_buffer')

        executors[self.operator] = f'./models/{self.operator}_postfail.zip'
        print(f"Executor file location {executors[self.operator]}")

        #Policy evaluation?

        return True

