# Recreate workspace
WS_ROOT="PathToWorkspaceRoot"

rm $WS_ROOT/src/CMakeLists.txt
cd $WS_ROOT/src/
catkin_init_workspace
cd $WS_ROOT
