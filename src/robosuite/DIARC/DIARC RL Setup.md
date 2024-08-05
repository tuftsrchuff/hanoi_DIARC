## Installing
1. Set up [DIARC](https://hrilab.tufts.edu:22280/diarc/diarc). See the DIARC readme for install instructions
2. Check out the branch `rl`
3. Run the command `./gradlew publishToMavenLocal`
4. Download the diarc-rl repo 

## Setup
1. In the DIARC readme, follow instructions for setting up Metric-FF. This will include creating/modifying `gradle.properties`.
2. In `trade.properties.default`, follow the instructions for making your own trade.properties file. The only thing you need to do is change `STARTDISCOVERY` to `true`

## Integrating
1. Instantiate the PythonRL object in your top level class & register it with TRADE. See the `main` method in diarc-rl to see how this is done.
2. Modify `callPolicy` and `learnPolicy` methods to suit your needs

## Running
1. Start things on the RL side. Ideally it will just be "waiting" for commands.
2. On the DIARC side, run the command `./gradlew launch -Pmain=edu.tufts.hrilab.config.RLConfig`

That should be it!