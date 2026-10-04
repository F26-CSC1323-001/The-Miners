# Web Backend
This branch contains the stuff built with Node Package Manager 

This is ran on a local machine with WSL Ubuntu via nvm (Node Version Manager)

Scaffolded the project with Vite, Vanilla JS

Basic Structure that will be worked with
parking-map/
├── index.html       ← entry point
├── src/
│   ├── main.js       ← your JS entry point
│   └── style.css
└── package.json

Rasberry Pi 400 will run receive the camera feed from the Samsung smart phone via IP, and will run the detection algorithm.

Vite frontend will need to fetch that data over HTTP.

I plan to use .pages.dev which is Cloudflare's own free subdomain for Cloudflare Pages
