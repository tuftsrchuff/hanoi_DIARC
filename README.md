# DIARC Integration for Tower of Hanoi
## Setup
Clone the hanoi branch of the [diarc-rl](https://hrilab.tufts.edu:22280/marlowfawn/diarc-rl/-/tree/hanoi?ref_type=heads) repo. Replace the diarc-rl folder located under hanoi_DIARC/src/robosuite/DIARC with the cloned diarc-rl repo. Follow the setup instructions located under the diarc-rl repo to set up DIARC and TRADE.

## Run
Run `MUJOCO_GL="glx" python diarc-rl.py` under hanoi_DIARC/src/robosuite/DIARC/diarc-rl to instantiate PythonRL object and register it with TRADE.

Then run `./gradlew launch -Pmain=edu.tufts.hrilab.config.RLConfig` on the DIARC side in a separate terminal. This will start the 

## Configuration
In order to render the robosuite environment during execution you must update the executor.execute_policy(symgoal) call in the callPolicy function of diarc-rl.py (under hanoi_DIARC/src/robosuite/DIARC/diarc-rl/) to executor.execute_policy(symgoal, render=True). If robosuite is not rendered the plan will still execute and print plan execution output to the terminal.

## Execution and learning
This is a Tower of Hanoi environment in Robosuite, with a goal of moving the blocks from the first peg to the third peg, obeying the rules of tower of hanoi. The planning and execution all operate within DIARC's cognitive architecture. Each step in the plan executes a pre-trained operator. If an operator fails, such as by introducing a novelty, DIARC will call a learner to learn a new operator to try to complete the plan.

