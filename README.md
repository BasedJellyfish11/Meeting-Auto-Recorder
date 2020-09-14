# Meeting Auto Recorder

A python tool to automatically join and record meetings of various kinds. Currently supports both Microsoft Teams and Blackboard Collaborate.

Assumes the meetings are the kind that repeats every week, such as classes, progress reports, or courses.

## Usage

Usage is simple: Included with the tool are sample JSON files of meetings of every kind supported. Edit said files with your text editor of choice, adding or removing meetings as you see fit, and filling out the fields with the characteristics of the meetings. 

Note that "duration" is given in hours (So an hour and a half will be 1.5), and that the start time is given as a date in ISO format.

Launch the released executable (or run main.py from the terminal of a system which has python and the dependencies installed if you so wish), then select your OBS install and the recording profile, scene collection and scene. Doing that and hitting the "Start" button should make it "just work (tm)".

Execution can be stopped by hitting the button again, which will change to say "Running" during execution.