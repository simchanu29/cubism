WS_ROOT="PathToWorkspaceRoot"

# Simulation for now
rosdep install --simulate --from-paths $WS_ROOT/src --ignore-src
echo -n "Do you want to install these packages (y/n)? "; read answer
if [ "$answer" != "y" ]; then return 0; fi # exit
