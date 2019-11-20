# Computer-Vision

In this class we were implementing opencv and taking input from cameras mounted on robots to have the robots perform certain actions.
Note that these were written for homemade robots at Montana State University, thus are unlikely to work elsewhere. For python 2.x.

helloHuman.py has the robot look around until it sees a face. Once it sees a face it will attempt to center it, moving the wheels and head until it has done so.

maestro.py is a support file written by Steven Jacobs -- Aug 2013 https://github.com/FRC4564/Maestro/.

lineFollow.py has the robot find a line of papers of a specific color and follow it untill the end.

marsRover.py implements all previous parts in order to simulate an automated digging action on mars. This includes following a line, lining up perpendicular to a colored line, find a face and line up with it.
