David S. — 07/12/2024 1:46 PM

1: do you want the targets to be moving or stationary?
2: if they are moving do you want actual AI-based tracking and firing control (will take longer to program) or just basic momentum
3: how many fighters are we talking about? because the more there are in the simulation the laggier it will be (doesnt matter if its on a powerful pc of course)
4: should I program a way to connect it to thorium so it can interact with things like lights, soind, ect?
5: how soon do you want this finished by?
6: what should the debris in the background be like? destroyed ships, or things like asteroids and planets?
7: how big of an area should the player/user be able to move around in?
8: what kind of computer is the server going to run on? windows, mac, linux?
9: should I use actual newtonian physics for the probe's movement, or is it ok if it is mostly constrained so it cant like roll over upside down, twist, then boost off in a random direction. I know that it should be as realistic as possible, I just also dont want to make it impossible to control

also, how do you want the app set up? I can go quite a few ways with it.
1: one file that runs on the web, with rendering, proccesing, essentially everything. just connect to the Ip and it runs
2: a file that runs on a server that handles above things, with a client app that streams the data to it. (client is an exe, server connects to client
3: same as 2, but the client is running on the web (least laggy option i think, the page will only have to handle a stream locally)
4: a plain .exe that has everything bundled together



The Space Place 🚀 — 07/13/2024 1:03 PM
It can't be an exe because that won't run on a chromebook - whatever we do needs to be chromebook compatible.
1) Stationary is fine.
2) ^
3) Not fighters, little harvesting drones. Like 20 of em.
4) Yes, for sounds, that'd be cool if we can automate the laser firing.
5) Soonish
6) Destroyed Ships
7) Should be constrained to the shipish
8) I don't know, you tell me what's best - can I run it off my mac in the control room?
9) Make it constrained.



c:\Users\david\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\blend2bam.exe src/models/ship1.blend src/models/ship1/ship1.bam --blender-dir "C:\Users\david\BLENDER\Versions\Blender2.93.9"