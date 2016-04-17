#!/usr/bin/env python

##############################
# RIPTIDE MAIN STATE MACHINE #
##############################

###########
# IMPORTS #
###########
# Include necessary libraries and your action and goal messages.

import roslib; roslib.load_manifest('riptide_autonomy')
import rospy
import smach
import smach_ros
import actionlib

from geometry_msgs.msg import Vector3
from riptide_msgs.msg import NavigateAction, NavigateGoal

#####################
# STATE DEFINITIONS #
#####################
# Define states that are not "Simple Action States" in here.

# Example:
class Foo(smach.State):
	# Define intitialization function. Runs on state creationg.
	def __init__(self):
		smach.State.__init__(self, outcomes=['succeeded', 'failed']);
	
	#Define execute function. Runs when state is active.
	def execute(self, userdata):
		return 'succeeded';

########
# MAIN #
########
# Entry point for the state machine.

DEFAULT_TIMEOUT = rospy.Duration(10);
ZERO_POSITION = Vector3(x = 0, y = 0, z = 0);


def main():
	rospy.init_node('STATE_MACHINE_NAME');
	
	Goal = NavigateGoal(searchGoal = "TASK_ONE", positionGoal = ZERO_POSITION, timeout = DEFAULT_TIMEOUT);
	
	# Create the state machine
	sm0 = smach.StateMachine(outcomes=['succeeded', 'aborted', 'preempted','failed']);
	# Add states
	with sm0:
		#  Normal state
		smach.StateMachine.add('FOO', Foo(), transitions={'succeeded':'GOTO_B', 'failed':'failed'});
		
		# GO TO B
		smach.StateMachine.add('GOTO_B', smach_ros.SimpleActionState('NavigateAction', NavigateAction, goal = Goal, result_key='B_Result',  output_keys=['B_Result']), transitions={'succeeded':'GOTO_C', 'aborted':'failed'});
		# GO TO C
		def GOTO_C_goalCB(userdata, currentGoal):
			currentGoal.positionGoal = userdata.C_In.realPosition;
			currentGoal.positionGoal.x += 2;
			currentGoal.positionGoal.y += 2;
			currentGoal.positionGoal.z += 2;
			currentGoal.searchGoal = "TASK_TWO";
			currentGoal.timeout = DEFAULT_TIMEOUT;
			return currentGoal;
			
		smach.StateMachine.add('GOTO_C', smach_ros.SimpleActionState('NavigateAction', NavigateAction, goal_cb = GOTO_C_goalCB, input_keys=['C_In']), transitions={'succeeded':'succeeded', 'aborted':'failed'}, remapping={'C_In':'B_Result'});
		
	# Run the state machine
	outcome = sm0.execute();
	
if __name__ == '__main__':
	main();