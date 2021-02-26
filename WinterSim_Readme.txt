--- Carla ScenarionRunner install ---

https://carla-scenariorunner.readthedocs.io/en/latest/getting_scenariorunner/

--- WinterSim Carla ScenarioRunner scenarios ---

Execute one of these scripts in Carla ScenarioRunner root folder.

python scenario_runner.py --scenario WinterSim_followscenario_01 --reloadWorld
python scenario_runner.py --scenario WinterSim_followscenario_02 --reloadWorld
python scenario_runner.py --scenario WinterSim_CutInFrom_right_Lane --reloadWorld
python scenario_runner.py --scenario WinterSim_Freeride_muonio_01 --reloadWorld


Open another terminal window and execute one of these in Carla ScenarioRunner root folder.

python wintersim_muonio_control.py --a --c --fr 1.0
python wintersim_muonio_control.py --a --c --fr 1.5
python wintersim_muonio_control.py --a --c --fr 1.75

This should open PyGame window and start the simulation. Make sure Scenario script is up and running before executing this.

Arguments:

--a 
Enables autopilot

--c
Enables constant velocity (25 km/h)

--fr [value]
Updates all actor vehicles wheel physics friction value. This way we can simulate road iciness. 
Lower value means more slippery road. 2.0 is default.

If you want drive completely manually remove --a and --c arguments.
python wintersim_muonio_control


Drive safe.


