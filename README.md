# Automatic instagram reels scrolling, with skipping, liking and following
This was used to display auto scrolling instagram reels 24/7 on a monitor below our living room TV, for maximum entertainment. Several commands are included, (which are currently executed via terminal, but if this project is picked back up, are intended to be executed via voice command) so that the household may curate its recommended reels.

Contains some basic selenium code for going to instagram reels, and automatically scrolling through each reel as they complete. Uses a multithreaded model so that the web driver can be accessed both on demand and on a timer.
Like all web automation, it's buggy.

You'll need to create a `.env` file with an EMAIL and PASSWORD for an instagram account. Do note instagram is pretty damn good at banning bot accounts. As long as you stick to reels and don't follow too many accounts too fast the account is unlikely to be banned. If the account is banned, the reels session will persist until you try to log back in-- so a good rule of thumb is to just never take down the bot.
