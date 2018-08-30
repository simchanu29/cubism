#!/usr/bin/env bash
WS_ROOT=$PWD
ERR="[ERROR]"
INF="[INFO]"
BASHRC_PATH=~/.bashrc

function main () {

    echo ""
    echo " === Installer install script === "
    echo ""

    # Check if sourced
    if [ "$0" != "/bin/bash" ]
    then
        echo "$ERR Script not running in parent shell. Run the script with source"
        echo "source install.sh"
        echo "exiting"
        return 1
    fi

    # Check if installed
    if [ -n  "`cat $BASHRC_PATH | grep "# ROS VSMARTH CONFIG"`" ]; then
        echo "$INF Already installed"
        return 0
    fi

    # Alias setup in bashrc
    echo "$INF Setting up aliases for workspace scripts"
    # echo "# ROS VSMARTH CONFIG">>$BASHRC_PATH
    # echo "alias vsmarth_install=\"source $WS_ROOT/install_files/install.sh\"">>$BASHRC_PATH
    # echo "alias vsmarth_init=\"source $WS_ROOT/install_files/init.sh\"">>$BASHRC_PATH
    # echo "alias vsmarth_launch=\"$WS_ROOT/install_files/launch.sh\"">>$BASHRC_PATH
    # echo "alias vsmarth_make=\"$WS_ROOT/install_files/make.sh\"">>$BASHRC_PATH

    source ~/.bashrc

    echo ""
    echo "run 'vsmarth_install'"
    echo "to install the workspace and all core dependencies"

}

main
