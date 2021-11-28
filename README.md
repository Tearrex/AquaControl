# AquaControl
 A mobile web application for your tech-savvy aquarium needs.

## What I wanted
Entertain myself during lockdown by automating some hobbies. I decided upon adding some lights to my aquarium which ultimately had me creating my own LED controller with a webserver for remote access. I tinkered with PHP in the past so I had a general idea of what I was doing, though I fancied a modern web framework this time.
## How I did it
I had a few Raspberry Pi's lying around, so I figured Python would be perfect for the job because I could self-host! It was between django and Flask—I chose the latter only because the pepper looked tasty. I like to start with the structure of the webpage so I can have a good idea of how I want to add the JavaScript functionality. I brushed up on my HTML skills and got to work.

The process of creating routes and handling data on the backend API was relatively straightforward once I figured out how requests work. GeeksForGeeks never fails to enthrall me with wisdom whenever I get stuck on something. I pondered making the webserver accessible on the internet so I also faced the challenge of user authentication. For this I wanted to include SQLite to store user credentials. I got lost in the cybersecurity aspect but I managed to add salt & pepper to passwords and store the hashes on a database. Most of the user interface communicates with the backend through AJAX calls.

## What I could improve
I have been learning a lot of cool new things since this was made. I can expand upon user authentication with Flask SQLAlchemy, redo styling with flex and SASS or utilize SMTP to email weekly reports. I'm experimenting with React now and want to give AquaControl a full makeover—maybe even learn React Native and Express.js to make an android application for my phone! I get carried away with ideas. For now, I want to polish what I already have.
