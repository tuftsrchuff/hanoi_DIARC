# DIARC Integration for Tower of Hanoi
## Setup
Clone the hanoi branch of the [diarc-rl](https://hrilab.tufts.edu:22280/marlowfawn/diarc-rl/-/tree/hanoi?ref_type=heads) repo. Replace the diarc-rl folder located under hanoi_DIARC/src/robosuite/DIARC with the cloned diarc-rl repo. Follow the setup instructions located at hanoi_DIARC/src/robosuite/DIARC/DIARC_setup.md.

## Run
Run `MUJOCO_GL="glx" python diarc-rl.py` under hanoi_DIARC/src/robosuite/DIARC/diarc-rl to instantiate PythonRL object and register it with TRADE. ``MUJOCO_GL="glx"` resolves issues related to running robosuite inside a JVM.

Then run `./gradlew launch -Pmain=edu.tufts.hrilab.config.RLConfig` on the DIARC side in a separate terminal.

## Configuration
In order to render the robosuite environment during execution you must update the executor.execute_policy(symgoal) call in the callPolicy function of diarc-rl.py (under hanoi_DIARC/src/robosuite/DIARC/diarc-rl/) to executor.execute_policy(symgoal, render=True). If robosuite is not rendered the plan will still execute and print plan execution output to the terminal.

## Execution and learning
This is a Tower of Hanoi environment in Robosuite, with a goal of moving the blocks from the first peg to the third peg, obeying the rules of tower of hanoi. The planning and execution all operate within DIARC's cognitive architecture. Each step in the plan executes a pre-trained operator. If an operator fails, such as by introducing a novelty, DIARC will call a learner to learn a new operator to try to complete the plan.

For executing in sim-to-real, only the ReachPick wrapper is set up to handle that. It uses the alive_reset parameter in its wrapper to make the reset a real position in space, instead of a hard reset in simulation.


## Troubleshooting
### Mujoco Errors
The GLFW library is not initialized - Run MUJOCO_GL="egl" python diarc-rl.py [Troubleshooting Link](https://github.com/Breakend/gym-extensions/issues/8). Likely an issue with non-NVIDIA GPUs.



'MjRenderContextOffscreen' object has no attribute 'con' - Run MUJOCO_GL="glx" python diarc-rl.py [Troubleshooting Link](https://github.com/ARISE-Initiative/robosuite/issues/469) This requires an Nvidia-GPU otherwise when running `./gradlew launch -Pmain=edu.tufts.hrilab.config.RLConfig` DIARC won't connect and error out with the message: "ERROR ActionContext -- No action found for event ?actor.callPolicy". This happens because Mujoco is trying to use offscreen rendering instead of onscreen. Not clear why the default is offscreen when running from DIARC.

err = EGL_NOT_INITIALIZED - Need to create a docker image using nvidia/cudagl@11.4.0-devel-ubuntu18.04 - [Troubleshooting Link](https://stackoverflow.com/questions/73281156/eglinitialize-failed-with-egl-not-initialized)


All of these issues are from running multiple instances of robosuite or rendering in DIARC. See the hanoi_reach_pick.reset_real function under src/robosuite/wrappers/behavior_cloning to reset without creating a new sim environment.